"""Scene, saved-scene, action-history, and image-serving routes.

All paths exchanged with the client are public URLs (relative to
client/public); anything the client sends is resolved through
server.paths.resolve_public_path, which rejects paths outside client/public.
"""
import base64
import io
import os
import re

from flask import Blueprint, jsonify, request, send_file, send_from_directory
from PIL import Image

from server.config import DATA_DIR, SERVER_IMDIR, STATIC_IMDIR
from server.http import get_json_body, require_fields
from server.paths import resolve_public_path, to_public_url
from server.services import scene_store
from utils.image import is_b64, makedir

bp = Blueprint("scenes", __name__)


@bp.route("/get_current_rendering")
def get_current_rendering():
    return scene_store.get_current_rendering()


@bp.route("/get_saved_renderings")
def get_saved_renderings():
    return scene_store.get_saved_renderings()


@bp.route("/save_rendering", methods=["POST"])
def save_rendering():
    body = get_json_body()
    rendering_path, textureparts_path = require_fields(
        body, "rendering_path", "textureparts_path")
    thumbnail_png = None
    thumbnail = body.get("thumbnail")
    if thumbnail:
        # dataURL from the Three.js canvas: "data:image/png;base64,...."
        thumbnail_png = base64.b64decode(thumbnail.split(",", 1)[-1])
    scene_store.add_to_saved_renderings(resolve_public_path(rendering_path),
                                        resolve_public_path(textureparts_path),
                                        STATIC_IMDIR, thumbnail_png=thumbnail_png)
    return scene_store.get_saved_renderings()


@bp.route("/apply_to_current_rendering", methods=["POST"])
def set_current_rendering():
    body = get_json_body()
    rendering_path, textureparts_path = require_fields(
        body, "rendering_path", "textureparts_path")
    scene_store.apply_to_current_rendering(resolve_public_path(rendering_path),
                                           resolve_public_path(textureparts_path))
    return scene_store.get_current_rendering()


@bp.route("/get_image", methods=["POST"])
def get_image():
    """Legacy image fetch. Images are served as plain static files now
    (GET /<public url>); this endpoint remains for base64 payloads."""
    img_data = require_fields(get_json_body(), "image_data")
    if is_b64(img_data):
        return send_file(io.BytesIO(base64.b64decode(img_data)), mimetype="image/png")
    return send_file(resolve_public_path(img_data))


@bp.route("/transfer_texture", methods=["POST"])
def transfer_texture():
    body = get_json_body()
    src_url, curr_textureparts_path = require_fields(
        body, "src_url", "curr_textureparts_path")
    src_path = resolve_public_path(src_url)
    curr_dir = os.path.dirname(resolve_public_path(curr_textureparts_path))

    src_dir = os.path.dirname(src_path)
    name, ext = os.path.splitext(os.path.basename(src_path))

    def _copy(suffix):
        src = os.path.join(src_dir, f"{name}{suffix}{ext}")
        if not os.path.isfile(src):
            return None
        dest = os.path.join(curr_dir, f"{name}{suffix}{ext}")
        if os.path.abspath(src) != os.path.abspath(dest):
            Image.open(src).save(dest)
        return to_public_url(dest)

    return jsonify({
        "img_url": _copy(""),
        "normal_url": _copy("_normal"),
        "height_url": _copy("_height"),
        "ao_url": _copy("_ao"),
    })


# --- HDRI environments (served from data/hdri, outside client/public) ---

_HDRI_DIR = os.path.join(DATA_DIR, "hdri")
_HDRI_EXTS = {".exr", ".hdr"}


@bp.route("/hdri_list")
def hdri_list():
    if not os.path.isdir(_HDRI_DIR):
        return jsonify({"hdris": []})
    names = sorted(f for f in os.listdir(_HDRI_DIR)
                   if os.path.splitext(f)[1].lower() in _HDRI_EXTS)
    return jsonify({"hdris": names})


@bp.route("/hdri/<path:name>")
def hdri_file(name):
    return send_from_directory(_HDRI_DIR, name)


def _no_material_path():
    return os.path.join(SERVER_IMDIR, "renderings", "current", "no_material.png")


def _resolve_or_default(path):
    """Resolve a client path, falling back to the neutral placeholder when
    it's empty or the file no longer exists (e.g. cleared action history)."""
    if path:
        resolved = resolve_public_path(path)
        if os.path.isfile(resolved):
            return resolved
    return _no_material_path()


@bp.route("/retrieve_textures_from_action_history", methods=["POST"])
def retrieve_textures_from_history():
    body = get_json_body()
    curr_dir = os.path.join(SERVER_IMDIR, "renderings", "current")

    result = {}
    for key, out_key in (("old_img_path", "updated_old_img_path"),
                         ("old_normal_path", "updated_old_normal_path"),
                         ("old_height_path", "updated_old_height_path")):
        src = _resolve_or_default(body.get(key))
        dest = os.path.join(curr_dir, os.path.basename(src))
        if os.path.abspath(src) != os.path.abspath(dest):
            Image.open(src).save(dest)
        result[out_key] = to_public_url(dest)
    return jsonify(result)


@bp.route("/add_old_and_new_textures_to_action_history", methods=["POST"])
def add_old_and_new_textures_to_history():
    body = get_json_body()
    history_index = require_fields(body, "current_history_index")
    history_dir = os.path.join(SERVER_IMDIR, "action_history", str(int(history_index)))
    makedir(os.path.join(history_dir, "old"))
    makedir(os.path.join(history_dir, "new"))

    result = {}
    for age in ("old", "new"):
        for kind in ("img", "normal", "height"):
            src = _resolve_or_default(body.get(f"{age}_{kind}_path"))
            dest = os.path.join(history_dir, age, os.path.basename(src))
            Image.open(src).save(dest)
            result[f"updated_{age}_{kind}_path"] = to_public_url(dest)
    return jsonify(result)


# --- Scene composition: uploads, manifest edits, object transforms ---

_ALLOWED_MODEL_EXTS = {".glb", ".gltf", ".obj", ".fbx", ".stl"}


def _safe_name(name):
    """Filesystem-safe object/file name (keep spaces, letters, digits)."""
    return re.sub(r"[^\w\- .()]", "_", name).strip() or "object"


@bp.route("/upload_model", methods=["POST"])
def upload_model():
    if "file" not in request.files:
        return jsonify({"error": "no file provided"}), 400
    file = request.files["file"]
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in _ALLOWED_MODEL_EXTS:
        allowed = ", ".join(sorted(_ALLOWED_MODEL_EXTS))
        return jsonify({"error": f"unsupported file type '{ext}'; upload one of {allowed}"}), 400

    object_name = _safe_name(request.form.get("object_name") or
                             os.path.splitext(os.path.basename(file.filename))[0])
    filename = _safe_name(os.path.basename(file.filename))

    dest_dir = os.path.join(SERVER_IMDIR, "renderings", "current", object_name)
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, filename)
    file.save(dest_path)

    return jsonify({"object_name": object_name, "model_path": to_public_url(dest_path)})


@bp.route("/update_manifest", methods=["POST"])
def update_manifest():
    texture_parts = require_fields(get_json_body(), "texture_parts")
    return scene_store.update_manifest(texture_parts)


@bp.route("/remove_object", methods=["POST"])
def remove_object():
    object_name = require_fields(get_json_body(), "object")
    texture_parts = scene_store.get_current_texture_parts() or {}
    texture_parts.pop(object_name, None)
    transforms = scene_store.get_transforms()
    if object_name in transforms:
        transforms.pop(object_name)
        scene_store.set_transforms(transforms)
    return scene_store.update_manifest(texture_parts)


@bp.route("/update_transforms", methods=["POST"])
def update_transforms():
    transforms = require_fields(get_json_body(), "transforms")
    scene_store.set_transforms(transforms)
    return jsonify({"transforms": scene_store.get_transforms()})

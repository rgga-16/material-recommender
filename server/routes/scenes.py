"""Scene, saved-scene, action-history, and image-serving routes."""
import base64
import io
import os
import re

from flask import Blueprint, jsonify, request, send_file
from PIL import Image

from server.config import CWD, SERVER_IMDIR, STATIC_IMDIR
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
    form_data = request.get_json()
    rendering_path = os.path.join(CWD, "client", "public", form_data["rendering_path"])
    thumbnail_png = None
    thumbnail = form_data.get("thumbnail")
    if thumbnail:
        # dataURL from the Three.js canvas: "data:image/png;base64,...."
        thumbnail_png = base64.b64decode(thumbnail.split(",", 1)[-1])
    scene_store.add_to_saved_renderings(rendering_path, form_data["textureparts_path"],
                                        STATIC_IMDIR, thumbnail_png=thumbnail_png)
    return scene_store.get_saved_renderings()


@bp.route("/apply_to_current_rendering", methods=["POST"])
def set_current_rendering():
    form_data = request.get_json()
    rendering_path = os.path.join(CWD, "client", "public", form_data["rendering_path"])
    scene_store.apply_to_current_rendering(rendering_path, form_data["textureparts_path"])
    return scene_store.get_current_rendering()


@bp.route("/get_image", methods=["POST"])
def get_image():
    img_data = request.get_json()["image_data"]
    if is_b64(img_data):
        return send_file(io.BytesIO(base64.b64decode(img_data)), mimetype="image/png")
    ext = os.path.splitext(img_data)[1][1:]
    return send_file(img_data, mimetype=f"image/{ext}")


@bp.route("/transfer_texture", methods=["POST"])
def transfer_texture():
    form_data = request.get_json()
    src_url = form_data["src_url"]
    curr_dir = os.path.dirname(form_data["curr_textureparts_path"])

    src_dir = os.path.dirname(src_url)
    name, ext = os.path.splitext(os.path.basename(src_url))

    def _copy(suffix):
        src = os.path.join(src_dir, f"{name}{suffix}{ext}")
        dest = os.path.join(curr_dir, f"{name}{suffix}{ext}")
        Image.open(src).save(dest)
        return dest

    return jsonify({
        "img_url": _copy(""),
        "normal_url": _copy("_normal"),
        "height_url": _copy("_height"),
    })


def _resolve_or_default(path, fallback):
    return path if path else fallback


@bp.route("/retrieve_textures_from_action_history", methods=["POST"])
def retrieve_textures_from_history():
    form_data = request.get_json()
    no_material = os.path.join(SERVER_IMDIR, "renderings", "current", "no_material.png")
    curr_dir = os.path.join(SERVER_IMDIR, "renderings", "current")

    result = {}
    for key, out_key in (("old_img_path", "updated_old_img_path"),
                         ("old_normal_path", "updated_old_normal_path"),
                         ("old_height_path", "updated_old_height_path")):
        src = _resolve_or_default(form_data[key], no_material)
        dest = os.path.join(curr_dir, os.path.basename(src))
        Image.open(src).save(dest)
        result[out_key] = dest
    return jsonify(result)


@bp.route("/add_old_and_new_textures_to_action_history", methods=["POST"])
def add_old_and_new_textures_to_history():
    form_data = request.get_json()
    no_material = os.path.join(SERVER_IMDIR, "renderings", "current", "no_material.png")
    history_dir = os.path.join(SERVER_IMDIR, "action_history",
                               str(form_data["current_history_index"]))
    makedir(os.path.join(history_dir, "old"))
    makedir(os.path.join(history_dir, "new"))

    result = {}
    for age in ("old", "new"):
        for kind in ("img", "normal", "height"):
            src = _resolve_or_default(form_data[f"{age}_{kind}_path"], no_material)
            dest = os.path.join(history_dir, age, os.path.basename(src))
            Image.open(src).save(dest)
            result[f"updated_{age}_{kind}_path"] = dest
    return jsonify(result)


# --- Scene composition: uploads, manifest edits, object transforms ---

_ALLOWED_MODEL_EXTS = {".glb", ".gltf"}


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
        return jsonify({"error": f"unsupported file type '{ext}'; upload .glb or .gltf"}), 400

    object_name = _safe_name(request.form.get("object_name") or
                             os.path.splitext(os.path.basename(file.filename))[0])
    filename = _safe_name(os.path.basename(file.filename))

    dest_dir = os.path.join(SERVER_IMDIR, "renderings", "current", object_name)
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, filename)
    file.save(dest_path)

    client_path = "/".join(["gen_images", "renderings", "current", object_name, filename])
    return jsonify({"object_name": object_name, "model_path": client_path})


@bp.route("/update_manifest", methods=["POST"])
def update_manifest():
    form_data = request.get_json()
    return scene_store.update_manifest(form_data["texture_parts"])


@bp.route("/remove_object", methods=["POST"])
def remove_object():
    form_data = request.get_json()
    object_name = form_data["object"]
    texture_parts = scene_store.get_current_texture_parts() or {}
    texture_parts.pop(object_name, None)
    transforms = scene_store.get_transforms()
    if object_name in transforms:
        transforms.pop(object_name)
        scene_store.set_transforms(transforms)
    return scene_store.update_manifest(texture_parts)


@bp.route("/update_transforms", methods=["POST"])
def update_transforms():
    form_data = request.get_json()
    scene_store.set_transforms(form_data["transforms"])
    return jsonify({"transforms": scene_store.get_transforms()})

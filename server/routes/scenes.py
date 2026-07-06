"""Scene, saved-scene, action-history, and image-serving routes."""
import base64
import io
import json
import os

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
    scene_store.add_to_saved_renderings(rendering_path, form_data["textureparts_path"],
                                        STATIC_IMDIR)
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


# --- Transitional shims (frontend still calls these; removed in Phase 4F) ---

@bp.route("/get_static_dir")
def get_static_dir():
    return STATIC_IMDIR


@bp.route("/use_chatgpt", methods=["GET"])
def use_chatgpt():
    return jsonify({"use_chatgpt": True})


@bp.route("/save_model", methods=["POST"])
def update_3d_model():
    form_data = request.get_json()
    server_model_path = os.path.join(STATIC_IMDIR, form_data["url"])
    server_model_path = os.path.splitext(server_model_path)[0] + ".gltf"
    with open(server_model_path, "w") as f:
        f.write(form_data["model"])
    return "ok"


@bp.route("/render", methods=["POST"])
def render():
    # Blender rendering removed; persist the manifest so the flow still works
    # until the frontend Render button is removed in Phase 4F.
    form_data = request.get_json()
    textureparts = form_data["textureparts"]
    curr_render_savedir = os.path.join(SERVER_IMDIR, "renderings", "current")
    for obj in textureparts:
        for part in textureparts[obj]:
            entry = textureparts[obj][part]
            if "model" in entry:
                model_filename = os.path.basename(entry["model"])
                entry["model"] = os.path.join(curr_render_savedir, obj, model_filename)
    with open(form_data["texturepartspath"], "w") as f:
        json.dump(textureparts, f, indent=4)
    return "ok"

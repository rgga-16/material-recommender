"""Scene state: the current scene manifest, saved scenes, and bootstrapping.

Replaces the old module-level current_texture_parts global and the startup
block in app.py. The manifest keeps the {object: {part: {props}}} shape that
the whole frontend (ThreeDDisplay, TexturePart, undo history) keys off.
"""
import copy
import json
import os
import shutil

from PIL import Image

from server.config import (CLIENT_IMDIR, MODELS_3D_DIR, SERVER_IMDIR,
                           DEMO_SCENE)
from utils.image import makedir, emptydir

_state = {
    "current_texture_parts": None,
    "latest_render_id": 0,
    "rendering_setup_path": None,
}


def get_current_texture_parts():
    return _state["current_texture_parts"]


def set_current_texture_parts(texture_parts):
    _state["current_texture_parts"] = copy.deepcopy(texture_parts)


def get_rendering_setup_path():
    return _state["rendering_setup_path"]


def _copy_image(src, dest_dir):
    dest = os.path.join(dest_dir, os.path.basename(src))
    Image.open(src).save(dest)
    return dest


def get_transforms():
    """Per-object placement transforms for the current scene (may be {})."""
    path = os.path.join(SERVER_IMDIR, "renderings", "current", "transforms.json")
    if os.path.isfile(path):
        with open(path) as f:
            return json.load(f)
    return {}


def set_transforms(transforms):
    path = os.path.join(SERVER_IMDIR, "renderings", "current", "transforms.json")
    with open(path, "w") as f:
        json.dump(transforms, f, indent=4)


def apply_to_current_rendering(renderpath, texture_parts_path):
    """Copy a scene's textures/models into the served current-scene dir."""
    curr_render_savedir = os.path.join(SERVER_IMDIR, "renderings", "current")
    curr_render_loaddir = os.path.join(CLIENT_IMDIR, "renderings", "current")
    makedir(curr_render_savedir)

    src_transforms = os.path.join(os.path.dirname(texture_parts_path), "transforms.json")
    if os.path.isfile(src_transforms) and \
            os.path.abspath(src_transforms) != os.path.abspath(
                os.path.join(curr_render_savedir, "transforms.json")):
        shutil.copy(src_transforms, os.path.join(curr_render_savedir, "transforms.json"))

    curr_render_path = os.path.join(curr_render_savedir, "rendering.png")
    curr_textureparts_path = os.path.join(curr_render_savedir, "object_part_material.json")

    texture_parts = json.load(open(texture_parts_path))

    for obj in texture_parts:
        for part in texture_parts[obj]:
            entry = texture_parts[obj][part]
            entry["mat_image_texture"] = _copy_image(entry["mat_image_texture"], curr_render_savedir)
            if "mat_normal_texture" in entry:
                entry["mat_normal_texture"] = _copy_image(entry["mat_normal_texture"], curr_render_savedir)
            if "mat_height_texture" in entry:
                entry["mat_height_texture"] = _copy_image(entry["mat_height_texture"], curr_render_savedir)
            if "model" in entry:
                model_filename = os.path.basename(entry["model"])
                destpath = os.path.join(curr_render_savedir, obj, model_filename)
                os.makedirs(os.path.dirname(destpath), exist_ok=True)
                shutil.copy(entry["model"], destpath)
                entry["model"] = os.path.join(curr_render_loaddir, obj, model_filename)

    set_current_texture_parts(texture_parts)
    with open(curr_textureparts_path, "w") as f:
        json.dump(texture_parts, f, indent=4)

    if renderpath and os.path.isfile(renderpath):
        shutil.copy(renderpath, curr_render_path)
    return curr_render_path, curr_textureparts_path


def add_to_saved_renderings(renderpath, texture_parts_path, static_imdir,
                            thumbnail_png=None):
    """Snapshot a scene (textures, maps, models, manifest) into saved/<id>/.

    thumbnail_png: optional raw PNG bytes (from the Three.js canvas) used as
    the scene thumbnail instead of copying renderpath.
    """
    render_id = _state["latest_render_id"]
    save_render_dir = os.path.join(SERVER_IMDIR, "renderings", "saved", str(render_id))
    save_render_path = os.path.join(save_render_dir, "rendering.png")
    save_textureparts_path = os.path.join(save_render_dir, "object_part_material.json")
    makedir(save_render_dir)

    src_transforms = os.path.join(os.path.dirname(texture_parts_path), "transforms.json")
    if os.path.isfile(src_transforms):
        shutil.copy(src_transforms, os.path.join(save_render_dir, "transforms.json"))

    texture_parts = json.load(open(texture_parts_path))
    for obj in texture_parts:
        for part in texture_parts[obj]:
            entry = texture_parts[obj][part]
            entry["mat_image_texture"] = _copy_image(entry["mat_image_texture"], save_render_dir)
            if "mat_normal_texture" in entry:
                entry["mat_normal_texture"] = _copy_image(entry["mat_normal_texture"], save_render_dir)
            if "mat_height_texture" in entry:
                entry["mat_height_texture"] = _copy_image(entry["mat_height_texture"], save_render_dir)
            if "model" in entry:
                model_path = entry["model"]
                model_filename = os.path.basename(model_path)
                destpath = os.path.join(save_render_dir, obj, model_filename)
                os.makedirs(os.path.dirname(destpath), exist_ok=True)
                # Model paths in the live manifest are client-relative; on
                # disk they live under client/public.
                full_model_path = model_path if os.path.isabs(model_path) \
                    else os.path.join(static_imdir, model_path)
                if not os.path.isfile(full_model_path):
                    full_model_path = model_path
                shutil.copy(full_model_path, destpath)
                entry["model"] = destpath

    with open(save_textureparts_path, "w") as f:
        json.dump(texture_parts, f, indent=4)
    if thumbnail_png:
        with open(save_render_path, "wb") as f:
            f.write(thumbnail_png)
    elif renderpath and os.path.isfile(renderpath):
        shutil.copy(renderpath, save_render_path)
    _state["latest_render_id"] += 1
    return save_render_path, save_textureparts_path


def get_saved_renderings():
    saved = []
    loaddir_client = os.path.join(CLIENT_IMDIR, "renderings", "saved")
    loaddir_server = os.path.join(SERVER_IMDIR, "renderings", "saved")
    dir_names = [f for f in os.listdir(loaddir_server)
                 if os.path.isdir(os.path.join(loaddir_server, f))]
    dir_names.reverse()
    for d in dir_names:
        textureparts_path = os.path.join(loaddir_server, d, "object_part_material.json")
        saved.append({
            "rendering_path": os.path.join(loaddir_client, d, "rendering.png"),
            "texture_parts": json.load(open(textureparts_path)),
            "textureparts_path": textureparts_path,
        })
    return {"saved_renderings": saved}


def get_current_rendering():
    curr_render_savedir = os.path.join(SERVER_IMDIR, "renderings", "current")
    current_textureparts_path = os.path.join(curr_render_savedir, "object_part_material.json")
    texture_parts = json.load(open(current_textureparts_path))
    return {
        "rendering_path": os.path.join(curr_render_savedir, "rendering.png"),
        "texture_parts": texture_parts,
        "textureparts_path": current_textureparts_path,
        "transforms": get_transforms(),
    }


def default_material_paths():
    """Absolute paths of the neutral placeholder texture set."""
    curr = os.path.join(SERVER_IMDIR, "renderings", "current")
    return {
        "mat_image_texture": os.path.join(curr, "no_material.png"),
        "mat_normal_texture": os.path.join(curr, "no_material_normal.png"),
        "mat_height_texture": os.path.join(curr, "no_material_height.png"),
    }


def update_manifest(texture_parts):
    """Persist a client-edited manifest, filling texture defaults for new
    (e.g. freshly uploaded) parts."""
    defaults = default_material_paths()
    for obj in texture_parts:
        for part in texture_parts[obj]:
            entry = texture_parts[obj][part]
            for key, value in defaults.items():
                if not entry.get(key):
                    entry[key] = value
    curr_render_savedir = os.path.join(SERVER_IMDIR, "renderings", "current")
    path = os.path.join(curr_render_savedir, "object_part_material.json")
    with open(path, "w") as f:
        json.dump(texture_parts, f, indent=4)
    set_current_texture_parts(texture_parts)
    return get_current_rendering()


def init(static_imdir):
    """Bootstrap the served scene dirs from the bundled demo scene."""
    demo_dir = os.path.join(MODELS_3D_DIR, DEMO_SCENE)
    render_dir = os.path.join(demo_dir, "renderings")
    _state["rendering_setup_path"] = os.path.join(demo_dir, "rendering_setup.json")

    emptydir(SERVER_IMDIR, delete_dirs=True) if os.path.isdir(SERVER_IMDIR) else None
    for sub in ("", "suggested", "feedbacked", "generated", "action_history",
                os.path.join("renderings", "current"), os.path.join("renderings", "saved")):
        makedir(os.path.join(SERVER_IMDIR, sub))

    init_texture_parts_path = os.path.join(render_dir, "current", "object_part_material.json")
    init_render_path = os.path.join(render_dir, "current", "rendering.png")
    apply_to_current_rendering(init_render_path, init_texture_parts_path)

    init_saved_dir = os.path.join(render_dir, "saved")
    if os.path.isdir(init_saved_dir):
        dir_names = sorted(int(f) for f in os.listdir(init_saved_dir)
                           if os.path.isdir(os.path.join(init_saved_dir, f)))
        for d in dir_names:
            dir_path = os.path.join(init_saved_dir, str(d))
            add_to_saved_renderings(os.path.join(dir_path, "rendering.png"),
                                    os.path.join(dir_path, "object_part_material.json"),
                                    static_imdir)

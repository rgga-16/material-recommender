"""Scene state: the current scene manifest, saved scenes, and bootstrapping.

The manifest keeps the {object: {part: {props}}} shape that the whole
frontend (ThreeDDisplay, TexturePart, undo history) keys off.

Path convention: every texture/model path stored in a manifest (and returned
to the client) is a public URL — forward slashes, relative to client/public,
e.g. "gen_images/renderings/current/wood_0.png" — so the browser can GET it
directly. Paths are resolved back to disk only at file-I/O boundaries.

Scenes persist across restarts: the current scene and saved scenes are kept;
only transient work dirs (generated candidates, suggestion previews, action
history) are cleared at startup. Both renderings/current and
renderings/saved/<id> are self-contained — every file they reference lives
inside them — which is what makes clearing the transient dirs safe.
"""
import copy
import json
import logging
import os
import shutil

from PIL import Image

from server.config import MODELS_3D_DIR, SERVER_IMDIR, DEMO_SCENE, STATIC_IMDIR
from server.paths import resolve_public_path, to_public_url, to_public_url_maybe
from utils.image import makedir, emptydir

log = logging.getLogger(__name__)

_TEXTURE_KEYS = ("mat_image_texture", "mat_normal_texture",
                 "mat_height_texture", "mat_ao_texture")

# Wiped at startup; nothing in renderings/ may reference files in these.
# generated/ persists — it backs the generation-history gallery.
_TRANSIENT_SUBDIRS = ("suggested", "feedbacked", "action_history")

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


def _resolve_src(path):
    """Resolve a manifest path to an existing file on disk.

    Accepts absolute paths, CWD-relative paths (the bundled demo manifests
    use "./data/..."), and public-URL paths.
    """
    if os.path.isfile(path):
        return path
    candidate = os.path.join(STATIC_IMDIR, path.lstrip("/\\"))
    if os.path.isfile(candidate):
        return candidate
    raise FileNotFoundError(f"scene file not found: {path}")


def _copy_image(src, dest_dir):
    src = _resolve_src(src)
    dest = os.path.join(dest_dir, os.path.basename(src))
    if os.path.abspath(src) != os.path.abspath(dest):
        Image.open(src).save(dest)
    return dest


def _load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _dump_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def _normalize_manifest(texture_parts):
    """Rewrite every path in a manifest to public-URL form (in place).

    Also migrates manifests written by older versions, which stored absolute
    Windows paths and backslash-separated model paths.
    """
    for obj in texture_parts:
        for part in texture_parts[obj]:
            entry = texture_parts[obj][part]
            for key in _TEXTURE_KEYS + ("model",):
                if entry.get(key):
                    entry[key] = to_public_url_maybe(entry[key])
    return texture_parts


def get_transforms():
    """Per-object placement transforms for the current scene (may be {})."""
    path = os.path.join(SERVER_IMDIR, "renderings", "current", "transforms.json")
    if os.path.isfile(path):
        return _load_json(path)
    return {}


def set_transforms(transforms):
    path = os.path.join(SERVER_IMDIR, "renderings", "current", "transforms.json")
    _dump_json(path, transforms)


def apply_to_current_rendering(renderpath, texture_parts_path):
    """Copy a scene's textures/models into the served current-scene dir."""
    curr_render_savedir = os.path.join(SERVER_IMDIR, "renderings", "current")
    makedir(curr_render_savedir)

    src_transforms = os.path.join(os.path.dirname(texture_parts_path), "transforms.json")
    if os.path.isfile(src_transforms) and \
            os.path.abspath(src_transforms) != os.path.abspath(
                os.path.join(curr_render_savedir, "transforms.json")):
        shutil.copy(src_transforms, os.path.join(curr_render_savedir, "transforms.json"))

    curr_render_path = os.path.join(curr_render_savedir, "rendering.png")
    curr_textureparts_path = os.path.join(curr_render_savedir, "object_part_material.json")

    texture_parts = _load_json(texture_parts_path)

    for obj in texture_parts:
        for part in texture_parts[obj]:
            entry = texture_parts[obj][part]
            for key in _TEXTURE_KEYS:
                if entry.get(key):
                    entry[key] = to_public_url(_copy_image(entry[key], curr_render_savedir))
            if entry.get("model"):
                model_src = _resolve_src(entry["model"])
                model_filename = os.path.basename(model_src)
                destpath = os.path.join(curr_render_savedir, obj, model_filename)
                os.makedirs(os.path.dirname(destpath), exist_ok=True)
                if os.path.abspath(model_src) != os.path.abspath(destpath):
                    shutil.copy(model_src, destpath)
                entry["model"] = to_public_url(destpath)

    set_current_texture_parts(texture_parts)
    _dump_json(curr_textureparts_path, texture_parts)

    if renderpath and os.path.isfile(renderpath):
        if os.path.abspath(renderpath) != os.path.abspath(curr_render_path):
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

    texture_parts = _load_json(texture_parts_path)
    for obj in texture_parts:
        for part in texture_parts[obj]:
            entry = texture_parts[obj][part]
            for key in _TEXTURE_KEYS:
                if entry.get(key):
                    entry[key] = to_public_url(_copy_image(entry[key], save_render_dir))
            if entry.get("model"):
                model_src = _resolve_src(entry["model"])
                model_filename = os.path.basename(model_src)
                destpath = os.path.join(save_render_dir, obj, model_filename)
                os.makedirs(os.path.dirname(destpath), exist_ok=True)
                shutil.copy(model_src, destpath)
                entry["model"] = to_public_url(destpath)

    _dump_json(save_textureparts_path, texture_parts)
    if thumbnail_png:
        with open(save_render_path, "wb") as f:
            f.write(thumbnail_png)
    elif renderpath and os.path.isfile(renderpath):
        shutil.copy(renderpath, save_render_path)
    _state["latest_render_id"] += 1
    return save_render_path, save_textureparts_path


def get_saved_renderings():
    saved = []
    loaddir_server = os.path.join(SERVER_IMDIR, "renderings", "saved")
    dir_ids = sorted((int(f) for f in os.listdir(loaddir_server)
                      if f.isdigit() and os.path.isdir(os.path.join(loaddir_server, f))),
                     reverse=True)
    for d in dir_ids:
        scene_dir = os.path.join(loaddir_server, str(d))
        textureparts_path = os.path.join(scene_dir, "object_part_material.json")
        if not os.path.isfile(textureparts_path):
            continue
        saved.append({
            "rendering_path": to_public_url(os.path.join(scene_dir, "rendering.png")),
            "texture_parts": _normalize_manifest(_load_json(textureparts_path)),
            "textureparts_path": to_public_url(textureparts_path),
        })
    return {"saved_renderings": saved}


def get_current_rendering():
    curr_render_savedir = os.path.join(SERVER_IMDIR, "renderings", "current")
    current_textureparts_path = os.path.join(curr_render_savedir, "object_part_material.json")
    texture_parts = _normalize_manifest(_load_json(current_textureparts_path))
    return {
        "rendering_path": to_public_url(os.path.join(curr_render_savedir, "rendering.png")),
        "texture_parts": texture_parts,
        "textureparts_path": to_public_url(current_textureparts_path),
        "transforms": get_transforms(),
    }


def default_material_paths():
    """Public URLs of the neutral placeholder texture set."""
    curr = os.path.join(SERVER_IMDIR, "renderings", "current")
    return {
        "mat_image_texture": to_public_url(os.path.join(curr, "no_material.png")),
        "mat_normal_texture": to_public_url(os.path.join(curr, "no_material_normal.png")),
        "mat_height_texture": to_public_url(os.path.join(curr, "no_material_height.png")),
    }


def update_manifest(texture_parts):
    """Persist a client-edited manifest.

    Fills texture defaults for new (e.g. freshly uploaded) parts, validates
    that every client-supplied path stays inside client/public, and copies
    any texture living in a transient dir (e.g. a freshly generated
    candidate) into renderings/current so the scene stays self-contained.
    """
    curr_render_savedir = os.path.join(SERVER_IMDIR, "renderings", "current")
    defaults = default_material_paths()
    for obj in texture_parts:
        for part in texture_parts[obj]:
            entry = texture_parts[obj][part]
            for key in _TEXTURE_KEYS:
                if not entry.get(key):
                    if key in defaults:
                        entry[key] = defaults[key]
                    continue
                resolved = resolve_public_path(entry[key])
                in_current = os.path.normcase(os.path.dirname(resolved)) == \
                    os.path.normcase(os.path.realpath(curr_render_savedir))
                if os.path.isfile(resolved) and not in_current:
                    resolved = _copy_image(resolved, curr_render_savedir)
                entry[key] = to_public_url_maybe(resolved)
            if entry.get("model"):
                # Validate only; models are placed under current/ by upload/apply.
                resolve_public_path(entry["model"])

    path = os.path.join(curr_render_savedir, "object_part_material.json")
    _dump_json(path, texture_parts)
    set_current_texture_parts(texture_parts)
    return get_current_rendering()


def _clean_transient():
    """Clear generated candidates/previews/history from previous sessions.

    Loose files at the top of gen_images/ (pre-overhaul generation output)
    are removed too; renderings/ and preset_cache/ are kept.
    """
    for sub in _TRANSIENT_SUBDIRS:
        subdir = os.path.join(SERVER_IMDIR, sub)
        if os.path.isdir(subdir):
            emptydir(subdir, delete_dirs=True)
        makedir(subdir)
    for fname in os.listdir(SERVER_IMDIR):
        fpath = os.path.join(SERVER_IMDIR, fname)
        if os.path.isfile(fpath):
            try:
                os.remove(fpath)
            except OSError:
                log.warning("could not remove stale file %s", fpath, exc_info=True)


def init(static_imdir):
    """Prepare the served scene dirs, bootstrapping from the bundled demo
    scene when there is no persisted scene from a previous session."""
    demo_dir = os.path.join(MODELS_3D_DIR, DEMO_SCENE)
    render_dir = os.path.join(demo_dir, "renderings")
    _state["rendering_setup_path"] = os.path.join(demo_dir, "rendering_setup.json")

    makedir(SERVER_IMDIR)
    for sub in (os.path.join("renderings", "current"), os.path.join("renderings", "saved")):
        makedir(os.path.join(SERVER_IMDIR, sub))
    _clean_transient()

    current_manifest = os.path.join(SERVER_IMDIR, "renderings", "current",
                                    "object_part_material.json")
    fresh = not os.path.isfile(current_manifest)
    if fresh:
        log.info("no persisted scene; bootstrapping demo scene %r", DEMO_SCENE)
        apply_to_current_rendering(
            os.path.join(render_dir, "current", "rendering.png"),
            os.path.join(render_dir, "current", "object_part_material.json"))
    else:
        set_current_texture_parts(_normalize_manifest(_load_json(current_manifest)))

    saved_dir = os.path.join(SERVER_IMDIR, "renderings", "saved")
    existing_ids = [int(f) for f in os.listdir(saved_dir)
                    if f.isdigit() and os.path.isdir(os.path.join(saved_dir, f))]
    _state["latest_render_id"] = max(existing_ids) + 1 if existing_ids else 0

    init_saved_dir = os.path.join(render_dir, "saved")
    if fresh and not existing_ids and os.path.isdir(init_saved_dir):
        for d in sorted(int(f) for f in os.listdir(init_saved_dir)
                        if os.path.isdir(os.path.join(init_saved_dir, f))):
            dir_path = os.path.join(init_saved_dir, str(d))
            add_to_saved_renderings(os.path.join(dir_path, "rendering.png"),
                                    os.path.join(dir_path, "object_part_material.json"),
                                    static_imdir)

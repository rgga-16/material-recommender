"""Preset PBR material routes.

Scans client/public/preset_materials/*/ at request time to discover the
available preset materials, instead of relying on a hardcoded dict.

Naming convention note: the drag/apply flow in ThreeDDisplay.svelte
(fullTextureTransferAlgorithm) derives a texture's normal/height map paths
purely by string convention: "<diffuse_path_without_ext>_normal.<ext>" and
"<diffuse_path_without_ext>_height.<ext>". Roughly half of the preset folders
already name their maps this way (e.g. "concrete01 diffuse 1k_normal.jpg"),
but the other half use a sibling-style name instead (e.g.
"Dirt04 diffuse 1k.jpg" + "Dirt04 normal 1k.jpg"), which the convention-based
derivation cannot resolve.

Since ThreeDDisplay.svelte is out of scope for this change, we normalize on
the server: for any preset that has a normal and/or height map, we cache
convention-named copies under client/public/gen_images/preset_cache/<folder>/
("<DisplayName>.<ext>", "<DisplayName>_normal.<ext>", "<DisplayName>_height.<ext>")
the first time they're requested, and return the cached paths instead of the
raw scanned ones. This keeps the frontend simple (it just uses whatever
"diffuse" path is returned, exactly like before) at the cost of a small
one-time disk copy per preset. Presets without any normal/height map are
returned as-is (no convention to satisfy).
"""
import os
import re
import shutil

from flask import Blueprint, jsonify

from server.config import SERVER_PRESET_IMDIR, STATIC_IMDIR
from server.paths import to_public_url

bp = Blueprint("presets", __name__)

_IMAGE_EXTS = {"jpg", "jpeg", "png"}

_PRESET_CACHE_DIR = os.path.join(STATIC_IMDIR, "gen_images", "preset_cache")


def _display_name(folder_name):
    """Turn a preset folder name into a human-friendly display name.

    e.g. "concrete01-1k" -> "Concrete01", "wood-05-1k" -> "Wood05",
    "leather-02" -> "Leather02"
    """
    stripped = re.sub(r"[-_]1[kK]$", "", folder_name)
    words = re.split(r"[-_]+", stripped)
    return " ".join(w[:1].upper() + w[1:].lower() for w in words if w)


def _find_maps(folder_path):
    """Find the diffuse/normal/height map filenames in a preset folder.

    Returns (diffuse, normal, height) filenames (any may be None for
    normal/height; diffuse may be None if no candidate was found).
    """
    diffuse = normal = height = None
    try:
        entries = sorted(os.listdir(folder_path))
    except OSError:
        return None, None, None

    for fname in entries:
        base, ext = os.path.splitext(fname)
        ext = ext[1:].lower()
        if ext not in _IMAGE_EXTS:
            continue
        lname = fname.lower()
        if diffuse is None and "diffuse" in lname:
            diffuse = fname
        elif normal is None and "normal" in lname:
            normal = fname
        elif height is None and "height" in lname:
            height = fname

    return diffuse, normal, height


def _cache_conventional_maps(folder_name, folder_path, diffuse, normal, height, display_name):
    """Copy diffuse/normal/height into a cache dir with convention-matching
    filenames, so downstream code that derives "<base>_normal.<ext>" /
    "<base>_height.<ext>" from the diffuse path works regardless of how the
    original preset files were named.

    Returns (diffuse_path, normal_path, height_path) absolute paths.
    """
    diffuse_ext = os.path.splitext(diffuse)[1][1:].lower()
    cache_dir = os.path.join(_PRESET_CACHE_DIR, folder_name)
    os.makedirs(cache_dir, exist_ok=True)

    def _copy_as(src_fname, suffix):
        src_path = os.path.join(folder_path, src_fname)
        dest_fname = f"{display_name}{suffix}.{diffuse_ext}"
        dest_path = os.path.join(cache_dir, dest_fname)
        if not os.path.exists(dest_path):
            src_ext = os.path.splitext(src_fname)[1][1:].lower()
            if src_ext == diffuse_ext:
                shutil.copyfile(src_path, dest_path)
            else:
                # Different source extension than the diffuse map; convert
                # so the destination extension matches (required for the
                # "<base>_suffix.<ext>" convention to resolve correctly).
                from PIL import Image
                Image.open(src_path).convert("RGB").save(dest_path)
        return dest_path

    diffuse_path = _copy_as(diffuse, "")
    normal_path = _copy_as(normal, "_normal") if normal else None
    height_path = _copy_as(height, "_height") if height else None
    return diffuse_path, normal_path, height_path


def _scan_preset_materials():
    presets = {}
    if not os.path.isdir(SERVER_PRESET_IMDIR):
        return presets

    for folder_name in sorted(os.listdir(SERVER_PRESET_IMDIR)):
        folder_path = os.path.join(SERVER_PRESET_IMDIR, folder_name)
        if not os.path.isdir(folder_path):
            continue

        diffuse, normal, height = _find_maps(folder_path)
        if diffuse is None:
            continue

        display_name = _display_name(folder_name)

        if normal or height:
            diffuse_path, normal_path, height_path = _cache_conventional_maps(
                folder_name, folder_path, diffuse, normal, height, display_name
            )
        else:
            diffuse_path = os.path.join(folder_path, diffuse)
            normal_path = None
            height_path = None

        presets[display_name] = {
            "diffuse": to_public_url(diffuse_path),
            "normal": to_public_url(normal_path) if normal_path else None,
            "height": to_public_url(height_path) if height_path else None,
        }

    return presets


@bp.route("/get_preset_materials", methods=["GET"])
def get_presets():
    return jsonify({"preset_materials": _scan_preset_materials()})

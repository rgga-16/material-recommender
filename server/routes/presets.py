"""Preset PBR material routes.

TEMPORARY (Phase 3D replaces the hardcoded dict with a dynamic scan of
client/public/preset_materials/).
"""
import os

from flask import Blueprint, jsonify

from server.config import SERVER_PRESET_IMDIR

bp = Blueprint("presets", __name__)

MATERIAL_PRESETS = {
    "Concrete": os.path.join(SERVER_PRESET_IMDIR, "concrete01-1k", "concrete01 diffuse 1k.jpg"),
    "Wood2": os.path.join(SERVER_PRESET_IMDIR, "wood-05-1k", "wood 05 diffuse 1k.jpg"),
    "Marble": os.path.join(SERVER_PRESET_IMDIR, "marble07-1k", "marble07 diffuse 1k.jpg"),
    "Marble2": os.path.join(SERVER_PRESET_IMDIR, "Marble01-1k", "Marble01 diffuse 1k.jpg"),
    "Fabric": os.path.join(SERVER_PRESET_IMDIR, "Fabric04-1k", "Fabric04 diffuse 1k.jpg"),
    "Plaster": os.path.join(SERVER_PRESET_IMDIR, "plaster04-1k", "plaster04 diffuse 1k.jpg"),
    "Tiles2": os.path.join(SERVER_PRESET_IMDIR, "tiles06-1k", "tiles06 diffuse 1k.jpg"),
}


@bp.route("/get_preset_materials", methods=["GET"])
def get_presets():
    return jsonify({"preset_material_paths": MATERIAL_PRESETS})

"""Texture generation and preset-material routes.

Phase 3B makes /generate_textures job-based on SD-Turbo; Phase 3D replaces
the hardcoded preset dict with a dynamic folder scan.
"""
import os

from flask import Blueprint, jsonify, request

from server.config import SERVER_IMDIR, SERVER_PRESET_IMDIR
from server.services import jobs, maps, texture_gen

bp = Blueprint("textures", __name__)

# TEMPORARY (Phase 3D replaces with a dynamic scan of preset_materials/)
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


def generate_and_save(texture_string, n, imsize):
    """Generate n textures + normal/height maps; returns result payload."""
    textures = texture_gen.generate(texture_string, n=n, imsize=imsize)
    texture_loadpaths = []
    for i, texture in enumerate(textures):
        filename = f"{texture_string}_{i}.png".replace(" ", "_").replace("/", "_")
        savepath = os.path.join(SERVER_IMDIR, filename)
        texture.save(savepath)
        maps.generate_normal_and_height(savepath)
        texture_loadpaths.append({"rendering": None, "texture": savepath})
    return {"results": texture_loadpaths}


@bp.route("/generate_textures", methods=["POST"])
def generate_textures_route():
    form_data = request.get_json()
    # TEMPORARY synchronous path; Phase 3B submits via jobs and returns job_id.
    return generate_and_save(form_data["texture_string"], form_data["n"],
                             form_data["imsize"])


@bp.route("/generate_similar_textures", methods=["POST"])
def generate_similar_textures():
    # DALL-E 2 image variations have no local equivalent; approximate with
    # fresh generations from the same prompt (frontend keeps working).
    form_data = request.get_json()
    result = generate_and_save(form_data["texture_string"], form_data["n"] - 1, 512)
    impath = form_data["impath"].replace(" ", "_")
    result["results"].insert(0, {"rendering": None, "texture": impath})
    return result


@bp.route("/jobs/<job_id>", methods=["GET"])
def get_job(job_id):
    job = jobs.get(job_id)
    if job is None:
        return jsonify({"error": "unknown job"}), 404
    return jsonify(job)

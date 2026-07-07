"""Texture generation routes.

Phase 3B makes /generate_textures job-based on SD-Turbo.
"""
import os

from flask import Blueprint, jsonify, request

from server.config import SERVER_IMDIR
from server.services import jobs, maps, texture_gen

bp = Blueprint("textures", __name__)


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
    job_id = jobs.submit(generate_and_save, form_data["texture_string"],
                         form_data["n"], form_data["imsize"])
    return jsonify({"job_id": job_id})


def generate_similar_and_save(texture_string, n, impath):
    """Generate n-1 fresh textures + normal/height maps, then prepend the
    original image; returns result payload."""
    result = generate_and_save(texture_string, n - 1, 512)
    result["results"].insert(0, {"rendering": None, "texture": impath})
    return result


@bp.route("/generate_similar_textures", methods=["POST"])
def generate_similar_textures():
    # DALL-E 2 image variations have no local equivalent; approximate with
    # fresh generations from the same prompt (frontend keeps working).
    form_data = request.get_json()
    impath = form_data["impath"].replace(" ", "_")
    job_id = jobs.submit(generate_similar_and_save, form_data["texture_string"],
                         form_data["n"], impath)
    return jsonify({"job_id": job_id})


@bp.route("/jobs/<job_id>", methods=["GET"])
def get_job(job_id):
    job = jobs.get(job_id)
    if job is None:
        return jsonify({"error": "unknown job"}), 404
    return jsonify(job)

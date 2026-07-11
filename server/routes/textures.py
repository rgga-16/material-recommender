"""Texture generation routes and the job status/SSE endpoints."""
import json
import os
import re

from flask import Blueprint, Response, jsonify

from server.config import SERVER_IMDIR
from server.http import get_json_body, require_fields
from server.paths import resolve_public_path, to_public_url
from server.services import jobs, maps, texture_gen

bp = Blueprint("textures", __name__)

_GENERATED_DIR = os.path.join(SERVER_IMDIR, "generated")


def safe_filename_stem(text):
    """A filesystem-safe filename stem derived from arbitrary prompt text.

    Dots are excluded: the client derives "<stem>_normal.<ext>" from the
    texture URL by splitting on the first ".".
    """
    stem = re.sub(r"[^\w\-()]", "_", text.strip()).strip("_")
    return (stem or "texture")[:80]


def _clamp_count(n, default=1, maximum=8):
    try:
        return max(1, min(int(n), maximum))
    except (TypeError, ValueError):
        return default


def generate_and_save(texture_string, n, imsize, job_id=None):
    """Generate n textures + normal/height maps; returns a result payload
    whose texture paths are public URLs."""
    n = _clamp_count(n)
    if job_id:
        jobs.set_progress(job_id, 0.05, "Generating textures...")
    textures = texture_gen.generate(texture_string, n=n, imsize=imsize)

    os.makedirs(_GENERATED_DIR, exist_ok=True)
    stem = safe_filename_stem(texture_string)
    texture_loadpaths = []
    for i, texture in enumerate(textures):
        savepath = os.path.join(_GENERATED_DIR, f"{stem}_{i}.png")
        texture.save(savepath)
        if job_id:
            jobs.set_progress(job_id, 0.5 + 0.5 * i / max(n, 1),
                              f"Deriving maps ({i + 1}/{n})...")
        maps.generate_normal_and_height(savepath)
        texture_loadpaths.append({"rendering": None, "texture": to_public_url(savepath)})
    return {"results": texture_loadpaths}


@bp.route("/generate_textures", methods=["POST"])
def generate_textures_route():
    body = get_json_body()
    texture_string, n, imsize = require_fields(body, "texture_string", "n", "imsize")
    job_id = jobs.submit(generate_and_save, texture_string, n, imsize,
                         pass_job_id=True)
    return jsonify({"job_id": job_id})


def generate_similar_and_save(texture_string, n, impath, job_id=None):
    """Generate n-1 fresh textures + normal/height maps, then prepend the
    original image; returns result payload."""
    result = generate_and_save(texture_string, _clamp_count(n) - 1, 512, job_id=job_id)
    result["results"].insert(0, {"rendering": None, "texture": impath})
    return result


@bp.route("/generate_similar_textures", methods=["POST"])
def generate_similar_textures():
    # True image variations are a possible future img2img feature; for now
    # approximate with fresh generations from the same prompt.
    body = get_json_body()
    texture_string, n, impath = require_fields(body, "texture_string", "n", "impath")
    impath = to_public_url(resolve_public_path(impath))
    job_id = jobs.submit(generate_similar_and_save, texture_string, n, impath,
                         pass_job_id=True)
    return jsonify({"job_id": job_id})


@bp.route("/jobs/<job_id>", methods=["GET"])
def get_job(job_id):
    job = jobs.get(job_id)
    if job is None:
        return jsonify({"error": "unknown job"}), 404
    return jsonify(job)


@bp.route("/jobs/<job_id>/events", methods=["GET"])
def job_events(job_id):
    """Server-Sent Events stream of a job's status until it finishes."""
    if jobs.get(job_id) is None:
        return jsonify({"error": "unknown job"}), 404

    def stream():
        version = -1
        while True:
            job, version = jobs.wait_for_update(job_id, version, timeout=25.0)
            if job is None:
                yield "event: gone\ndata: {}\n\n"
                return
            yield f"data: {json.dumps(job)}\n\n"
            if job["status"] in ("done", "error"):
                return

    return Response(stream(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache",
                             "X-Accel-Buffering": "no"})

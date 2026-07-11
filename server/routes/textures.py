"""Texture generation routes, the persistent gallery, texture-set export,
and the job status/SSE endpoints."""
import io
import json
import os
import re
import zipfile

from flask import Blueprint, Response, jsonify, request, send_file

from server.config import SERVER_IMDIR
from server.http import get_json_body, require_fields
from server.paths import resolve_public_path, to_public_url
from server.services import jobs, maps, texture_gen

bp = Blueprint("textures", __name__)

_GENERATED_DIR = os.path.join(SERVER_IMDIR, "generated")
_MAP_SUFFIXES = ("_normal", "_height", "_ao")


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


def _parse_seed(value):
    """Non-negative int seed, else None (random)."""
    try:
        seed = int(value)
    except (TypeError, ValueError):
        return None
    return seed if seed >= 0 else None


def _save_textures(images, texture_string, seed=None, job_id=None,
                   progress_from=0.5):
    """Save generated images + derived maps; returns the result payload."""
    os.makedirs(_GENERATED_DIR, exist_ok=True)
    stem = safe_filename_stem(texture_string)
    n = max(len(images), 1)
    texture_loadpaths = []
    for i, texture in enumerate(images):
        savepath = os.path.join(_GENERATED_DIR, f"{stem}_{i}.png")
        texture.save(savepath)
        if job_id:
            jobs.set_progress(job_id, progress_from + (1 - progress_from) * i / n,
                              f"Deriving maps ({i + 1}/{len(images)})...")
        maps.generate_normal_and_height(savepath)
        texture_loadpaths.append({
            "rendering": None,
            "texture": to_public_url(savepath),
            "seed": None if seed is None else seed + i,
        })
    return {"results": texture_loadpaths}


def generate_and_save(texture_string, n, imsize, seed=None, job_id=None):
    """Generate n textures + normal/height/AO maps; returns a result payload
    whose texture paths are public URLs."""
    n = _clamp_count(n)
    if job_id:
        jobs.set_progress(job_id, 0.05, "Generating textures...")
    images = texture_gen.generate(texture_string, n=n, imsize=imsize, seed=seed)
    return _save_textures(images, texture_string, seed=seed, job_id=job_id)


@bp.route("/generate_textures", methods=["POST"])
def generate_textures_route():
    body = get_json_body()
    texture_string, n, imsize = require_fields(body, "texture_string", "n", "imsize")
    job_id = jobs.submit(generate_and_save, texture_string, n, imsize,
                         seed=_parse_seed(body.get("seed")), pass_job_id=True)
    return jsonify({"job_id": job_id})


def generate_similar_and_save(texture_string, n, impath, seed=None, job_id=None):
    """img2img variations of an existing texture: generate n-1 variations,
    then prepend the original image."""
    from PIL import Image

    n = _clamp_count(n)
    result = {"results": []}
    if n > 1:
        if job_id:
            jobs.set_progress(job_id, 0.05, "Generating variations...")
        init_image = Image.open(resolve_public_path(impath))
        images = texture_gen.generate_variations(init_image, texture_string,
                                                 n=n - 1, seed=seed)
        result = _save_textures(images, f"{texture_string}_var", seed=seed,
                                job_id=job_id)
    result["results"].insert(0, {"rendering": None, "texture": impath,
                                 "seed": None})
    return result


@bp.route("/generate_similar_textures", methods=["POST"])
def generate_similar_textures():
    body = get_json_body()
    texture_string, n, impath = require_fields(body, "texture_string", "n", "impath")
    impath = to_public_url(resolve_public_path(impath))
    job_id = jobs.submit(generate_similar_and_save, texture_string, n, impath,
                         seed=_parse_seed(body.get("seed")), pass_job_id=True)
    return jsonify({"job_id": job_id})


def _is_map_file(stem):
    return any(stem.endswith(suffix) for suffix in _MAP_SUFFIXES)


@bp.route("/generated_textures", methods=["GET"])
def generated_textures():
    """The persistent generation gallery: every generated diffuse texture,
    newest first."""
    if not os.path.isdir(_GENERATED_DIR):
        return jsonify({"results": []})
    entries = []
    for fname in os.listdir(_GENERATED_DIR):
        stem, ext = os.path.splitext(fname)
        if ext.lower() != ".png" or _is_map_file(stem):
            continue
        fpath = os.path.join(_GENERATED_DIR, fname)
        entries.append((os.path.getmtime(fpath), fpath))
    entries.sort(reverse=True)
    return jsonify({"results": [{"rendering": None, "texture": to_public_url(p)}
                                for _, p in entries]})


@bp.route("/export_texture_set", methods=["GET"])
def export_texture_set():
    """Download a texture and its derived maps as one zip."""
    texture = request.args.get("texture", "")
    diffuse = resolve_public_path(texture)
    if not os.path.isfile(diffuse):
        return jsonify({"error": "texture not found"}), 404

    stem, ext = os.path.splitext(os.path.basename(diffuse))
    directory = os.path.dirname(diffuse)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(diffuse, f"{stem}/albedo{ext}")
        for suffix, out in (("_normal", "normal"), ("_height", "height"),
                            ("_ao", "ao")):
            src = os.path.join(directory, f"{stem}{suffix}{ext}")
            if os.path.isfile(src):
                zf.write(src, f"{stem}/{out}{ext}")
    buffer.seek(0)
    return send_file(buffer, mimetype="application/zip", as_attachment=True,
                     download_name=f"{stem}_textures.zip")


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

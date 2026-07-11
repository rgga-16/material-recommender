"""LLM assistant routes: chat, suggestions, feedback, brainstorming, translate.

Backed by a local Ollama LLM (server/services/llm.py). Chat endpoints accept
an optional "session_id" so each browser session gets its own conversation.
Endpoints that also run texture generation (/suggest_materials,
/feedback_materials) submit a background job and return {"job_id": ...};
poll GET /jobs/<id> or subscribe to GET /jobs/<id>/events for the result.
"""
import functools
import json
import logging
import os
import uuid

from flask import Blueprint, Response, jsonify, request

from server.config import SERVER_IMDIR
from server.http import get_json_body, require_fields
from server.paths import to_public_url
from server.routes.textures import generate_and_save, safe_filename_stem
from server.services import jobs, llm, prompts, texture_gen

bp = Blueprint("assistant", __name__)

log = logging.getLogger(__name__)

_SSE_HEADERS = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}


def _handle_llm_errors(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except llm.LLMUnavailableError as e:
            return jsonify({"error": str(e)}), 503
    return wrapper


def _session_id(body=None):
    if body and body.get("session_id"):
        return str(body["session_id"])
    return request.args.get("session_id") or llm.DEFAULT_SESSION


@bp.route("/init_query", methods=["GET"])
@_handle_llm_errors
def init_query():
    response = llm.init_conversation(_session_id())
    return jsonify({"response": response, "role": "assistant"})


@bp.route("/query", methods=["POST"])
@_handle_llm_errors
def query():
    body = get_json_body()
    prompt = require_fields(body, "prompt")
    response = llm.query(prompt, session_id=_session_id(body),
                         role=body.get("role", "user"))
    return jsonify({"response": response, "role": "assistant"})


@bp.route("/query_stream", methods=["POST"])
def query_stream():
    """Streaming chat turn (SSE over a POST body). Events carry
    {"delta": chunk} then {"done": true}, or {"error": message}."""
    body = get_json_body()
    prompt = require_fields(body, "prompt")
    session_id = _session_id(body)
    role = body.get("role", "user")

    def stream():
        try:
            for chunk in llm.query_stream(prompt, session_id=session_id, role=role):
                yield f"data: {json.dumps({'delta': chunk})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except llm.LLMUnavailableError as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(stream(), mimetype="text/event-stream", headers=_SSE_HEADERS)


@bp.route("/translate", methods=["POST"])
@_handle_llm_errors
def translate():
    body = get_json_body()
    text, target_lang, source_lang = require_fields(
        body, "text", "target_lang", "source_lang")
    translated = llm.chat(
        [{"role": "user", "content": prompts.translate_prompt(text, target_lang, source_lang)}],
        system=prompts.TRANSLATE_SYSTEM_PROMPT,
        temperature=0.1,
    )
    return jsonify({"text": translated.strip()})


def _generate_suggested_texture(name):
    """Generate a small preview texture (with maps) for a suggested material."""
    result = generate_and_save(f"{name}, texture map, seamless", 1, 512)
    return result["results"][0]["texture"]


def _suggest_materials_job(prompt_text, design_brief, job_id=None):
    if job_id:
        jobs.set_progress(job_id, 0.05, "Asking the assistant for materials...")
    parsed = llm.generate_json(
        [{"role": "user", "content": prompts.suggest_materials_prompt(prompt_text, design_brief)}],
        schema=prompts.MATERIALS_SCHEMA,
        system=prompts.SYSTEM_PROMPT,
    )
    intro_text = parsed.get("intro_text", "")
    materials = [m for m in parsed.get("materials", []) if m.get("name")]

    suggested_materials = []
    for i, item in enumerate(materials):
        name = item.get("name", "")
        if job_id:
            jobs.set_progress(job_id, 0.2 + 0.8 * i / max(len(materials), 1),
                              f"Generating {name} preview...")
        filepath = _generate_suggested_texture(name)
        suggested_materials.append({"name": name, "reason": item.get("reason", ""),
                                    "filepath": filepath})

    return {"intro_text": intro_text, "role": "assistant",
            "suggested_materials": suggested_materials}


@bp.route("/suggest_materials", methods=["POST"])
def suggest_materials():
    body = get_json_body()
    prompt_text = require_fields(body, "prompt")
    job_id = jobs.submit(_suggest_materials_job, prompt_text, body.get("context"),
                         pass_job_id=True)
    return jsonify({"job_id": job_id})


@bp.route("/suggest_colors", methods=["POST"])
@_handle_llm_errors
def suggest_colors():
    body = get_json_body()
    prompt_text = require_fields(body, "prompt")
    parsed = llm.generate_json(
        [{"role": "user", "content": prompts.suggest_color_palettes_prompt(prompt_text)}],
        schema=prompts.COLOR_PALETTES_SCHEMA,
        system=prompts.SYSTEM_PROMPT,
    )
    palettes = parsed.get("color_palettes", [])
    formatted_palettes = []
    for cp in palettes:
        formatted_palettes.append({
            "name": cp.get("name", ""),
            "description": cp.get("description", ""),
            "codes": cp.get("codes", []),
        })
    return jsonify({"intro_text": "", "role": "assistant",
                    "suggested_color_palettes": formatted_palettes})


@bp.route("/get_texture_prompts", methods=["POST"])
@_handle_llm_errors
def get_texture_prompts():
    body = get_json_body()
    parsed = llm.generate_json(
        [{"role": "user", "content": prompts.get_texture_prompts_prompt(
            body.get("prompt", ""), body.get("n", 3), body.get("design_brief"))}],
        schema=prompts.TEXTURE_PROMPTS_SCHEMA,
        system=prompts.SYSTEM_PROMPT,
    )
    texture_prompts = parsed.get("texture_prompts", [])
    return jsonify({"texture_prompts": texture_prompts})


@bp.route("/get_materials", methods=["POST"])
@_handle_llm_errors
def get_materials():
    body = get_json_body()
    parsed = llm.generate_json(
        [{"role": "user", "content": prompts.get_materials_prompt(
            body.get("material_name", ""), body.get("prompt", ""),
            body.get("n", 3), body.get("design_brief"))}],
        schema=prompts.MATERIALS_TEXTUREBASED_SCHEMA,
        system=prompts.SYSTEM_PROMPT,
    )
    return jsonify({"materials": parsed.get("suggested_materials", []),
                    "explanations": parsed.get("explanations", []),
                    "prompts": parsed.get("texture_prompts", [])})


def _generate_color_preview(name):
    """Photorealistic preview image for a non-material suggestion, saved
    under the transient feedbacked/ dir; returns its public URL."""
    image = texture_gen.generate(f"{name}, photorealistic", n=1, imsize=512)[0]
    feedback_dir = os.path.join(SERVER_IMDIR, "feedbacked")
    os.makedirs(feedback_dir, exist_ok=True)
    savepath = os.path.join(
        feedback_dir, f"{safe_filename_stem(name)}_{uuid.uuid4().hex[:8]}.png")
    image.save(savepath)
    return to_public_url(savepath)


def _feedback_materials_job(material_name, object_name, part_name,
                            attached_parts, design_brief, job_id=None):
    if job_id:
        jobs.set_progress(job_id, 0.05, "Asking the assistant for feedback...")
    parsed = llm.generate_json(
        [{"role": "user", "content": prompts.feedback_materials_prompt(
            material_name, object_name, part_name,
            attached_parts=attached_parts, design_brief=design_brief)}],
        schema=prompts.FEEDBACK_SCHEMA,
        system=prompts.SYSTEM_PROMPT,
    )

    suggestions_dict = {}
    for aspect in prompts.FEEDBACK_ASPECTS:
        aspect_data = parsed.get(aspect, {})
        suggestions_dict[aspect] = {
            "feedback": aspect_data.get("feedback", ""),
            "suggestions": aspect_data.get("suggestions", []),
        }

    all_suggestions = [s for aspect in suggestions_dict
                       for s in suggestions_dict[aspect]["suggestions"] if len(s) >= 2]
    for i, suggestion in enumerate(all_suggestions):
        name, kind = suggestion[0], suggestion[1]
        if job_id:
            jobs.set_progress(job_id, 0.2 + 0.8 * i / max(len(all_suggestions), 1),
                              f"Generating {name} preview...")
        try:
            if kind == "material":
                result = generate_and_save(f"{name}, texture map, seamless", 1, 512)
                suggestion.append(result["results"][0]["texture"])
            else:
                suggestion.append(_generate_color_preview(name))
        except Exception:
            # Don't let a failed preview generation take down the whole
            # feedback response.
            log.warning("preview generation failed for %r", name, exc_info=True)
            suggestion.append(None)

    return {"intro_text": "", "unformatted_response": "",
            "formatted_response": suggestions_dict, "references": "",
            "role": "assistant"}


@bp.route("/feedback_materials", methods=["POST"])
def feedback_materials():
    body = get_json_body()
    material_name, object_name, part_name = require_fields(
        body, "material_name", "object_name", "part_name")
    job_id = jobs.submit(_feedback_materials_job, material_name, object_name,
                         part_name, body.get("attached_parts"),
                         body.get("design_brief"), pass_job_id=True)
    return jsonify({"job_id": job_id})


@bp.route("/brainstorm_prompt_keywords", methods=["POST"])
@_handle_llm_errors
def brainstorm_prompt_keywords():
    body = get_json_body()
    texture_string = require_fields(body, "texture_string")
    parsed = llm.generate_json(
        [{"role": "user", "content": prompts.brainstorm_prompt_keywords_prompt(
            texture_string, body.get("design_brief"))}],
        schema=prompts.TEXTURE_KEYWORDS_SCHEMA,
        system=prompts.SYSTEM_PROMPT,
    )
    keywords = parsed.get("keywords", [])
    return jsonify({"brainstormed_prompt_keywords": keywords, "role": "assistant"})


@bp.route("/brainstorm_material_queries", methods=["GET"])
@_handle_llm_errors
def brainstorm_material_queries():
    parsed = llm.generate_json(
        [{"role": "user", "content": prompts.MATERIALS_SUGGESTION_PROMPT}],
        schema=prompts.MATERIAL_QUERIES_SCHEMA,
        system=prompts.SYSTEM_PROMPT,
    )
    prompts_list = parsed.get("prompts", [])
    return jsonify({"prompts": prompts_list, "role": "assistant"})

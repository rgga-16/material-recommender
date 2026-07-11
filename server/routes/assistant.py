"""LLM assistant routes: chat, smart suggestions, scene feedback, translate.

Backed by a local Ollama LLM (server/services/llm.py). The design brief is
always injected server-side (system prompt), and every suggestion/chat turn
is grounded with best-effort DuckDuckGo web search. Requests may carry a
"screenshot" (canvas dataURL); when the multimodal model is pulled it is
forwarded so the assistant can see the scene's visual state.

Chat endpoints accept an optional "session_id" so each browser session gets
its own conversation. Endpoints that also run texture generation (/suggest,
/feedback_scene) submit a background job and return {"job_id": ...}; poll
GET /jobs/<id> or subscribe to GET /jobs/<id>/events for the result.
"""
import functools
import json
import logging
import os
import threading
import uuid

from flask import Blueprint, Response, jsonify, request

from server.config import SERVER_IMDIR
from server.http import get_json_body, require_fields
from server.paths import to_public_url
from server.routes.textures import generate_and_save, safe_filename_stem
from server.services import (design_brief, jobs, llm, material_props, prompts,
                             scene_store, texture_gen, websearch)

bp = Blueprint("assistant", __name__)

log = logging.getLogger(__name__)

_SSE_HEADERS = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}

# Cap on preview images generated for one feedback/suggest response, so a
# chatty LLM can't queue minutes of SD work.
_MAX_PREVIEWS = 4


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


def _system():
    return prompts.system_prompt(design_brief.get_brief())


def _screenshot_b64(body):
    """Raw base64 (no data: prefix) of a canvas-dataURL screenshot, or None."""
    shot = body.get("screenshot") or ""
    if "," in shot:
        shot = shot.split(",", 1)[1]
    return shot.strip() or None


def _vision_images(screenshot):
    """The images list for llm calls, only when the vision model can take it."""
    if screenshot and llm.vision_available():
        return [screenshot]
    return None


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------

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
    web_context, references = websearch.context_block(prompt)
    response = llm.query(prompt, session_id=_session_id(body),
                         role=body.get("role", "user"), context=web_context)
    if references:
        response += f"\n\n{references}"
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
            web_context, references = websearch.context_block(prompt)
            for chunk in llm.query_stream(prompt, session_id=session_id,
                                          role=role, context=web_context):
                yield f"data: {json.dumps({'delta': chunk})}\n\n"
            if references:
                refs_delta = json.dumps({"delta": "\n\n" + references})
                yield f"data: {refs_delta}\n\n"
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


# ---------------------------------------------------------------------------
# Smart suggest (single entry point: materials, colors, or both)
# ---------------------------------------------------------------------------

_COLOR_WORDS = ("color", "colour", "palette", "hue", "shade", "scheme")
_MATERIAL_WORDS = ("material", "fabric", "wood", "metal", "stone", "finish",
                   "texture", "leather", "surface")


def _classify_intent(prompt_text):
    """materials | colors | both — cheap keyword check, LLM tie-break."""
    lower = prompt_text.lower()
    wants_colors = any(w in lower for w in _COLOR_WORDS)
    wants_materials = any(w in lower for w in _MATERIAL_WORDS)
    if wants_colors and wants_materials:
        return "both"
    if wants_colors:
        return "colors"
    if wants_materials:
        return "materials"
    try:
        parsed = llm.generate_json(
            [{"role": "user", "content": prompts.classify_suggest_intent_prompt(prompt_text)}],
            schema=prompts.INTENT_SCHEMA,
            temperature=0.0,
        )
        intent = parsed.get("intent", "materials")
        return intent if intent in prompts.SUGGEST_INTENTS else "materials"
    except Exception:
        return "materials"


def _generate_suggested_texture(name):
    """Generate a small preview texture (with maps) for a suggested material."""
    result = generate_and_save(f"{name}, texture map, seamless", 1, 512,
                               enrich=False)
    return result["results"][0]["texture"]


def _suggest_job(prompt_text, screenshot, job_id=None):
    if job_id:
        jobs.set_progress(job_id, 0.02, "Understanding your request...")
    intent = _classify_intent(prompt_text)

    if job_id:
        jobs.set_progress(job_id, 0.08, "Searching the web...")
    web_context, references = websearch.context_block(prompt_text)

    images = _vision_images(screenshot)
    system = _system()
    result = {"intent": intent, "role": "assistant", "references": references,
              "intro_text": ""}
    intros = []

    if intent in ("materials", "both"):
        if job_id:
            jobs.set_progress(job_id, 0.15, "Asking the assistant for materials...")
        parsed = llm.generate_json(
            [{"role": "user", "content": prompts.suggest_materials_prompt(
                prompt_text, web_context=web_context,
                describe_scene=bool(images))}],
            schema=prompts.MATERIALS_SCHEMA,
            system=system,
            images=images,
        )
        intros.append(parsed.get("intro_text", ""))
        materials = [m for m in parsed.get("materials", []) if m.get("name")]

        suggested_materials = []
        for i, item in enumerate(materials[:_MAX_PREVIEWS]):
            name = item.get("name", "")
            if job_id:
                jobs.set_progress(job_id, 0.3 + 0.6 * i / max(len(materials), 1),
                                  f"Generating {name} preview...")
            filepath = _generate_suggested_texture(name)
            suggested_materials.append({"name": name,
                                        "reason": item.get("reason", ""),
                                        "filepath": filepath})
        result["suggested_materials"] = suggested_materials

    if intent in ("colors", "both"):
        if job_id:
            jobs.set_progress(job_id, 0.9 if intent == "both" else 0.3,
                              "Asking the assistant for color palettes...")
        parsed = llm.generate_json(
            [{"role": "user", "content": prompts.suggest_color_palettes_prompt(
                prompt_text, web_context=web_context,
                describe_scene=bool(images))}],
            schema=prompts.COLOR_PALETTES_SCHEMA,
            system=system,
            images=images,
        )
        result["suggested_color_palettes"] = [
            {"name": cp.get("name", ""),
             "description": cp.get("description", ""),
             "codes": cp.get("codes", [])}
            for cp in parsed.get("color_palettes", [])
        ]

    result["intro_text"] = " ".join(t for t in intros if t)
    return result


@bp.route("/suggest", methods=["POST"])
def suggest():
    body = get_json_body()
    prompt_text = require_fields(body, "prompt")
    job_id = jobs.submit(_suggest_job, prompt_text, _screenshot_b64(body),
                         pass_job_id=True)
    return jsonify({"job_id": job_id})


# ---------------------------------------------------------------------------
# Per-part prompt ideas (chips shown when a part is selected)
# ---------------------------------------------------------------------------

_part_prompts_cache = {}
_part_prompts_lock = threading.Lock()


@bp.route("/suggest_part_prompts", methods=["POST"])
@_handle_llm_errors
def suggest_part_prompts():
    body = get_json_body()
    object_name, part_name = require_fields(body, "object_name", "part_name")
    material_name = body.get("material_name") or ""
    brief = design_brief.get_brief()
    cache_key = (object_name, part_name, material_name, hash(brief))
    with _part_prompts_lock:
        cached = _part_prompts_cache.get(cache_key)
    if cached is not None:
        return jsonify(cached)

    parsed = llm.generate_json(
        [{"role": "user", "content": prompts.suggest_part_prompts_prompt(
            object_name, part_name, material_name)}],
        schema=prompts.PART_PROMPTS_SCHEMA,
        system=prompts.system_prompt(brief),
        temperature=0.5,
    )
    result = {
        "material_prompts": [p for p in parsed.get("material_prompts", []) if p][:3],
        "color_prompts": [p for p in parsed.get("color_prompts", []) if p][:3],
        "role": "assistant",
    }
    if result["material_prompts"] or result["color_prompts"]:
        with _part_prompts_lock:
            _part_prompts_cache[cache_key] = result
    return jsonify(result)


# ---------------------------------------------------------------------------
# Material intelligence (auto finish/tiling after a texture is applied)
# ---------------------------------------------------------------------------

@bp.route("/material_properties", methods=["POST"])
def material_properties():
    material_name = require_fields(get_json_body(), "material_name")
    return jsonify(material_props.properties_for(material_name))


# ---------------------------------------------------------------------------
# Texture prompt / material exploration helpers (preset library)
# ---------------------------------------------------------------------------

@bp.route("/get_texture_prompts", methods=["POST"])
@_handle_llm_errors
def get_texture_prompts():
    body = get_json_body()
    parsed = llm.generate_json(
        [{"role": "user", "content": prompts.get_texture_prompts_prompt(
            body.get("prompt", ""), body.get("n", 3))}],
        schema=prompts.TEXTURE_PROMPTS_SCHEMA,
        system=_system(),
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
            body.get("n", 3))}],
        schema=prompts.MATERIALS_TEXTUREBASED_SCHEMA,
        system=_system(),
    )
    return jsonify({"materials": parsed.get("suggested_materials", []),
                    "explanations": parsed.get("explanations", []),
                    "prompts": parsed.get("texture_prompts", [])})


# ---------------------------------------------------------------------------
# Proactive scene feedback (always grounded in the design brief)
# ---------------------------------------------------------------------------

def _generate_color_preview(name):
    """Photorealistic preview image for a non-material suggestion, saved
    under the transient feedbacked/ dir; returns its public URL."""
    image = texture_gen.generate(f"{name}, photorealistic", n=1, imsize=512,
                                 enrich=False)[0]
    feedback_dir = os.path.join(SERVER_IMDIR, "feedbacked")
    os.makedirs(feedback_dir, exist_ok=True)
    savepath = os.path.join(
        feedback_dir, f"{safe_filename_stem(name)}_{uuid.uuid4().hex[:8]}.png")
    image.save(savepath)
    return to_public_url(savepath)


def _scene_summary():
    """Compact text listing of the current scene's parts and materials."""
    texture_parts = scene_store.get_current_texture_parts() or {}
    lines = []
    for obj, parts in texture_parts.items():
        for part, entry in parts.items():
            if not isinstance(entry, dict):
                continue
            mat = entry.get("mat_name") or "none"
            detail = f"material {mat}" if mat != "none" else "untextured"
            color = entry.get("color")
            if color:
                detail += f", color {color}"
            if entry.get("metalness"):
                detail += f", metalness {entry['metalness']}"
            label = obj if obj == part else f"{obj} / {part}"
            lines.append(f"- {label}: {detail}")
    return "\n".join(lines)


def _feedback_scene_job(screenshot, job_id=None):
    if job_id:
        jobs.set_progress(job_id, 0.05, "Reviewing the scene...")
    summary = _scene_summary()
    if not summary:
        return {"summary": "", "observations": [], "references": "",
                "role": "assistant"}

    brief = design_brief.get_brief()
    web_context, references = websearch.context_block(
        f"{brief.strip().splitlines()[0]} materials")
    images = _vision_images(screenshot)

    parsed = llm.generate_json(
        [{"role": "user", "content": prompts.feedback_scene_prompt(
            summary, has_image=bool(images), web_context=web_context)}],
        schema=prompts.SCENE_FEEDBACK_SCHEMA,
        system=prompts.system_prompt(brief),
        images=images,
    )

    observations = []
    for obs in parsed.get("observations", []):
        if not obs.get("text"):
            continue
        observations.append({
            "aspect": obs.get("aspect", ""),
            "text": obs["text"],
            "suggestions": [s for s in obs.get("suggestions", [])
                            if isinstance(s, dict) and s.get("name")],
        })

    n_previews = 0
    all_suggestions = [s for obs in observations for s in obs["suggestions"]]
    for i, suggestion in enumerate(all_suggestions):
        if n_previews >= _MAX_PREVIEWS:
            suggestion["filepath"] = None
            continue
        name, kind = suggestion["name"], suggestion.get("kind", "other")
        if job_id:
            jobs.set_progress(job_id, 0.4 + 0.55 * i / max(len(all_suggestions), 1),
                              f"Generating {name} preview...")
        try:
            if kind == "material":
                suggestion["filepath"] = _generate_suggested_texture(name)
            else:
                suggestion["filepath"] = _generate_color_preview(name)
            n_previews += 1
        except Exception:
            # Don't let a failed preview generation take down the whole
            # feedback response.
            log.warning("preview generation failed for %r", name, exc_info=True)
            suggestion["filepath"] = None

    return {"summary": parsed.get("summary", ""), "observations": observations,
            "references": references, "role": "assistant"}


@bp.route("/feedback_scene", methods=["POST"])
def feedback_scene():
    body = get_json_body()
    job_id = jobs.submit(_feedback_scene_job, _screenshot_b64(body),
                         pass_job_id=True)
    return jsonify({"job_id": job_id})


# ---------------------------------------------------------------------------
# Brainstorming (starter chips for the chat composer)
# ---------------------------------------------------------------------------

@bp.route("/brainstorm_material_queries", methods=["GET"])
@_handle_llm_errors
def brainstorm_material_queries():
    parsed = llm.generate_json(
        [{"role": "user", "content": prompts.MATERIALS_SUGGESTION_PROMPT}],
        schema=prompts.MATERIAL_QUERIES_SCHEMA,
        system=_system(),
    )
    prompts_list = parsed.get("prompts", [])
    return jsonify({"prompts": prompts_list, "role": "assistant"})

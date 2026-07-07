"""LLM assistant routes: chat, suggestions, feedback, brainstorming, translate.

Backed by a local Ollama LLM (server/services/llm.py) instead of the OpenAI
API. Route URLs and response JSON shapes are kept identical to the previous
OpenAI-backed implementation so the frontend does not need any changes.
"""
import functools

from flask import Blueprint, jsonify, request

from server.routes.textures import generate_and_save
from server.services import llm, prompts

bp = Blueprint("assistant", __name__)


def _handle_llm_errors(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except llm.LLMUnavailableError as e:
            return jsonify({"error": str(e)}), 503
    return wrapper


@bp.route("/init_query", methods=["GET"])
@_handle_llm_errors
def init_query():
    response = llm.init_conversation()
    return jsonify({"response": response, "role": "assistant"})


@bp.route("/query", methods=["POST"])
@_handle_llm_errors
def query():
    form_data = request.get_json()
    response = llm.query(form_data["prompt"], form_data.get("role", "user"))
    return jsonify({"response": response, "role": "assistant"})


@bp.route("/translate", methods=["POST"])
@_handle_llm_errors
def translate():
    form_data = request.get_json()
    text = form_data["text"]
    target_lang = form_data["target_lang"]
    source_lang = form_data["source_lang"]
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


@bp.route("/suggest_materials", methods=["POST"])
@_handle_llm_errors
def suggest_materials():
    form_data = request.get_json()
    design_brief = form_data.get("context")
    parsed = llm.generate_json(
        [{"role": "user", "content": prompts.suggest_materials_prompt(form_data["prompt"], design_brief)}],
        schema=prompts.MATERIALS_SCHEMA,
        system=prompts.SYSTEM_PROMPT,
    )
    intro_text = parsed.get("intro_text", "")
    materials = parsed.get("materials", [])

    suggested_materials = []
    for item in materials:
        name = item.get("name", "")
        reason = item.get("reason", "")
        if not name:
            continue
        filepath = _generate_suggested_texture(name)
        suggested_materials.append({"name": name, "reason": reason, "filepath": filepath})

    return jsonify({"intro_text": intro_text, "role": "assistant",
                    "suggested_materials": suggested_materials})


@bp.route("/suggest_colors", methods=["POST"])
@_handle_llm_errors
def suggest_colors():
    form_data = request.get_json()
    parsed = llm.generate_json(
        [{"role": "user", "content": prompts.suggest_color_palettes_prompt(form_data["prompt"])}],
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
    form_data = request.get_json()
    # image_path is accepted for backwards compatibility but ignored: the
    # local model is text-only.
    design_brief = form_data.get("design_brief")
    parsed = llm.generate_json(
        [{"role": "user", "content": prompts.get_texture_prompts_prompt(
            form_data.get("prompt", ""), form_data.get("n", 3), design_brief)}],
        schema=prompts.TEXTURE_PROMPTS_SCHEMA,
        system=prompts.SYSTEM_PROMPT,
    )
    texture_prompts = parsed.get("texture_prompts", [])
    return jsonify({"texture_prompts": texture_prompts})


@bp.route("/get_materials", methods=["POST"])
@_handle_llm_errors
def get_materials():
    form_data = request.get_json()
    # image_path is accepted for backwards compatibility but ignored: the
    # local model is text-only.
    design_brief = form_data.get("design_brief")
    parsed = llm.generate_json(
        [{"role": "user", "content": prompts.get_materials_prompt(
            form_data.get("material_name", ""), form_data.get("prompt", ""),
            form_data.get("n", 3), design_brief)}],
        schema=prompts.MATERIALS_TEXTUREBASED_SCHEMA,
        system=prompts.SYSTEM_PROMPT,
    )
    materials = parsed.get("suggested_materials", [])
    explanations = parsed.get("explanations", [])
    texture_prompts = parsed.get("texture_prompts", [])
    return jsonify({"materials": materials, "explanations": explanations,
                    "prompts": texture_prompts})


@bp.route("/feedback_materials", methods=["POST"])
@_handle_llm_errors
def feedback_materials():
    form_data = request.get_json()
    parsed = llm.generate_json(
        [{"role": "user", "content": prompts.feedback_materials_prompt(
            form_data["material_name"], form_data["object_name"], form_data["part_name"],
            attached_parts=form_data.get("attached_parts"),
            design_brief=form_data.get("design_brief"))}],
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

    for aspect in suggestions_dict:
        for suggestion in suggestions_dict[aspect]["suggestions"]:
            if len(suggestion) < 2:
                continue
            name, kind = suggestion[0], suggestion[1]
            try:
                if kind == "material":
                    result = generate_and_save(f"{name}, texture map, seamless", 1, 512)
                    savepath = result["results"][0]["texture"]
                    suggestion.append(savepath)
                else:
                    from server.services import texture_gen
                    from utils.image import im_2_b64
                    image = texture_gen.generate(f"{name}, photorealistic", n=1, imsize=512)[0]
                    suggestion.append(im_2_b64(image).decode("utf-8"))
            except Exception:
                # Don't let a failed preview generation take down the whole
                # feedback response.
                suggestion.append(None)

    return jsonify({"intro_text": "", "unformatted_response": "",
                    "formatted_response": suggestions_dict, "references": "",
                    "role": "assistant"})


@bp.route("/brainstorm_prompt_keywords", methods=["POST"])
@_handle_llm_errors
def brainstorm_prompt_keywords():
    form_data = request.get_json()
    parsed = llm.generate_json(
        [{"role": "user", "content": prompts.brainstorm_prompt_keywords_prompt(
            form_data["texture_string"], form_data.get("design_brief"))}],
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

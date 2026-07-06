"""LLM assistant routes: chat, suggestions, feedback, brainstorming, translate.

TEMPORARY (Phase 2): still delegates to the legacy OpenAI-based models/llm/gpt3
module (imported lazily so the server starts without an API key). Phase 3C
replaces the internals with the local Ollama service.
"""
import os
import time

from flask import Blueprint, jsonify, request

from server.config import SERVER_IMDIR, SERVER_PRESET_IMDIR
from server.routes.textures import generate_and_save
from server.services import maps
from utils.image import im_2_b64, impath_2_b64

bp = Blueprint("assistant", __name__)


def _gpt3():
    import models.llm.gpt3 as gpt3
    return gpt3


@bp.route("/init_query", methods=["GET"])
def init_query():
    response = _gpt3().init_query()
    return jsonify({"response": response, "role": "assistant"})


@bp.route("/query", methods=["POST"])
def query():
    form_data = request.get_json()
    response = _gpt3().query(form_data["prompt"], form_data["role"])
    return jsonify({"response": response, "role": "assistant"})


@bp.route("/translate", methods=["POST"])
def translate():
    form_data = request.get_json()
    translated = _gpt3().translate(form_data["text"], form_data["target_lang"],
                                   form_data["source_lang"])
    return jsonify({"text": translated})


def _generate_suggested_texture(name, savedir):
    """Generate a small preview texture (with maps) for a suggested material."""
    result = generate_and_save(f"{name}, texture map, seamless", 1, 512)
    return result["results"][0]["texture"]


@bp.route("/suggest_materials", methods=["POST"])
def suggest_materials():
    form_data = request.get_json()
    intro_text, suggested = _gpt3().suggest_materials_2(
        form_data["prompt"], role=form_data["role"],
        use_internet=form_data["use_internet"], design_brief=form_data["context"])
    suggested_materials = []
    for name in suggested:
        filepath = _generate_suggested_texture(name, os.path.join(SERVER_IMDIR, "suggested"))
        suggested_materials.append({"name": name, "reason": suggested[name],
                                    "filepath": filepath})
    return jsonify({"intro_text": intro_text, "role": "assistant",
                    "suggested_materials": suggested_materials})


@bp.route("/suggest_colors", methods=["POST"])
def suggest_colors():
    form_data = request.get_json()
    intro_text, palettes = _gpt3().suggest_color_palettes(
        form_data["prompt"], role=form_data["role"],
        use_internet=form_data["use_internet"])
    return jsonify({"intro_text": intro_text, "role": "assistant",
                    "suggested_color_palettes": palettes})


@bp.route("/get_texture_prompts", methods=["POST"])
def get_texture_prompts():
    form_data = request.get_json()
    interior_b64 = impath_2_b64(os.path.join(SERVER_PRESET_IMDIR, "visual_context.png"))
    texture_prompts = _gpt3().suggest_texture_prompts(
        form_data["prompt"], form_data["n"], impath_2_b64(form_data["image_path"]),
        form_data["design_brief"], interior_state=interior_b64)
    return jsonify({"texture_prompts": texture_prompts})


@bp.route("/get_materials", methods=["POST"])
def get_materials():
    form_data = request.get_json()
    interior_b64 = impath_2_b64(os.path.join(SERVER_PRESET_IMDIR, "visual_context.png"))
    materials, explanations, prompts = _gpt3().suggest_materials_texturebased(
        form_data["material_name"], form_data["prompt"], form_data["n"],
        impath_2_b64(form_data["image_path"]), form_data["design_brief"],
        interior_state=interior_b64)
    return jsonify({"materials": materials, "explanations": explanations,
                    "prompts": prompts})


@bp.route("/feedback_materials", methods=["POST"])
def feedback_materials():
    form_data = request.get_json()
    intro_text, response, suggestions_dict, references = _gpt3().provide_material_feedback2(
        form_data["material_name"], form_data["object_name"], form_data["part_name"],
        use_internet=False, attached_parts=form_data["attached_parts"],
        design_brief=form_data["design_brief"])

    for aspect in suggestions_dict:
        for suggestion in suggestions_dict[aspect]["suggestions"]:
            name, kind = suggestion[0], suggestion[1]
            if kind == "material":
                result = generate_and_save(f"{name}, texture map, seamless", 1, 512)
                savepath = result["results"][0]["texture"]
                suggestion.append(savepath)
            else:
                from server.services import texture_gen
                image = texture_gen.generate(f"{name}, photorealistic", n=1, imsize=512)[0]
                suggestion.append(im_2_b64(image).decode("utf-8"))

    return jsonify({"intro_text": intro_text, "unformatted_response": response,
                    "formatted_response": suggestions_dict, "references": "",
                    "role": "assistant"})


@bp.route("/brainstorm_prompt_keywords", methods=["POST"])
def brainstorm_prompt_keywords():
    form_data = request.get_json()
    keywords = _gpt3().brainstorm_prompt_keywords(form_data["texture_string"],
                                                  form_data["design_brief"])
    return jsonify({"brainstormed_prompt_keywords": keywords, "role": "assistant"})


@bp.route("/brainstorm_material_queries", methods=["GET"])
def brainstorm_material_queries():
    prompts = _gpt3().brainstorm_material_queries()
    return jsonify({"prompts": prompts, "role": "assistant"})

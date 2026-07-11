"""Prompt text and JSON-schema definitions for the local LLM service.

The design brief is injected once, into the system prompt, by every caller
(build it with system_prompt(design_brief.get_brief())); individual task
prompts only add task-specific instructions and optional web-search context.
"""

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

BASE_SYSTEM_PROMPT = '''You are an interior and furniture design expert with expert knowledge of materials. Your role is to:

1) Suggest materials and color palettes when asked, depending on the criteria to suggest them.
2) Provide feedback on materials and designs when asked.

Always ground your answers in the client's design brief below. Keep your replies concise.'''


def system_prompt(design_brief: str | None = None) -> str:
    if not design_brief:
        return BASE_SYSTEM_PROMPT
    return f"{BASE_SYSTEM_PROMPT}\n\n--- DESIGN BRIEF ---\n{design_brief}"


def with_web_context(text: str, web_context: str | None) -> str:
    if web_context:
        text += f"\n\n{web_context}"
    return text


# ---------------------------------------------------------------------------
# Translation
# ---------------------------------------------------------------------------

TRANSLATE_SYSTEM_PROMPT = '''Act as a professional translator between English and Japanese.
Use polite and formal language, and keep terms relevant to the given context.
Reply with ONLY the translated text, nothing else.'''


def translate_prompt(text: str, target_lang: str, source_lang: str) -> str:
    return (
        f"Translate the following text from {source_lang} to {target_lang}. "
        f"If it is already in {target_lang}, keep the original text unchanged. "
        f"Do not say anything else apart from the translated text.\n\n{text}"
    )


# ---------------------------------------------------------------------------
# Smart suggest: intent classification
# ---------------------------------------------------------------------------

SUGGEST_INTENTS = ["materials", "colors", "both"]

INTENT_SCHEMA = {
    "type": "object",
    "properties": {
        "intent": {"type": "string", "enum": SUGGEST_INTENTS},
    },
    "required": ["intent"],
}


def classify_suggest_intent_prompt(prompt: str) -> str:
    return (
        f'A user of an interior-design tool typed this request:\n"{prompt}"\n\n'
        f'Decide what they are asking for: "materials" (physical materials, '
        f'fabrics, woods, finishes...), "colors" (color palettes, hues, '
        f'schemes), or "both". Answer with just the intent.'
    )


# ---------------------------------------------------------------------------
# Material suggestions
# ---------------------------------------------------------------------------

MATERIALS_SCHEMA = {
    "type": "object",
    "properties": {
        "intro_text": {"type": "string"},
        "materials": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "reason": {"type": "string"},
                },
                "required": ["name", "reason"],
            },
        },
    },
    "required": ["intro_text", "materials"],
}


def suggest_materials_prompt(prompt: str, n: int = 4,
                             web_context: str | None = None,
                             describe_scene: bool = False) -> str:
    text = f"{prompt}\n\nSuggest {n} suitable materials that fit the design brief."
    if describe_scene:
        text += (
            "\n\nAn image of the current state of the 3D scene is attached; "
            "take the visible materials and colors into account."
        )
    text += (
        "\n\nReturn a short intro sentence and a list of materials, each with a name "
        "and a brief, concrete reason (1-2 sentences)."
    )
    return with_web_context(text, web_context)


# ---------------------------------------------------------------------------
# Color palettes
# ---------------------------------------------------------------------------

COLOR_PALETTES_SCHEMA = {
    "type": "object",
    "properties": {
        "color_palettes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "codes": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": ["name", "description", "codes"],
            },
        }
    },
    "required": ["color_palettes"],
}


def suggest_color_palettes_prompt(prompt: str, web_context: str | None = None,
                                  describe_scene: bool = False) -> str:
    text = f"{prompt}. Suggest a few color palettes that fit the design brief."
    if describe_scene:
        text += (
            "\n\nAn image of the current state of the 3D scene is attached; "
            "take the visible materials and colors into account."
        )
    text += (
        "\n\nFor each palette, give a name, a brief description, and a list of "
        "hex color codes in the form #RRGGBB (e.g. #FFC300)."
    )
    return with_web_context(text, web_context)


# ---------------------------------------------------------------------------
# Texture prompt enrichment (replaces the old manual keywords feature)
# ---------------------------------------------------------------------------

ENRICHED_PROMPT_SCHEMA = {
    "type": "object",
    "properties": {
        "prompt": {"type": "string"},
    },
    "required": ["prompt"],
}


def enrich_texture_prompt(material: str) -> str:
    return (
        f'I am generating a seamless texture map image of "{material}" with a '
        f'text-to-image model. Rewrite this into one detail-rich, comma-separated '
        f'prompt (at most 20 words) that names a specific type of {material} and '
        f'describes its surface detail, color, and finish. Where relevant, match '
        f'the design brief. Keep the word "{material}" in the prompt. Do not '
        f'mention objects, rooms, scenes, or lighting setups.'
    )


TEXTURE_PROMPTS_SCHEMA = {
    "type": "object",
    "properties": {
        "texture_prompts": {
            "type": "array",
            "items": {"type": "string"},
        },
        "reasons": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": ["texture_prompts", "reasons"],
}


def get_texture_prompts_prompt(prompt: str, n: int) -> str:
    text = (
        f"Please make {n} varying text prompts that can be used with a text-to-image "
        f"generator to create detailed, flat, seamless texture map images."
    )
    if prompt:
        text += f"\n\nUse the following as guidance for the prompts:\n{prompt}"
    text += (
        "\n\nConsider the design brief for context, but don't explicitly mention "
        "it in the texture prompts. For each prompt, also give a brief reason."
    )
    return text


MATERIALS_TEXTUREBASED_SCHEMA = {
    "type": "object",
    "properties": {
        "suggested_materials": {
            "type": "array",
            "items": {"type": "string"},
        },
        "explanations": {
            "type": "array",
            "items": {"type": "string"},
        },
        "texture_prompts": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": ["suggested_materials", "explanations", "texture_prompts"],
}


def get_materials_prompt(material_name: str, prompt: str, n: int) -> str:
    text = (
        f"Based on the material \"{material_name}\", please suggest {n} materials that "
        f"are similar to it"
    )
    if prompt:
        text += f" and that also address the following query: {prompt}"
    text += (
        ". If the material name is generic (e.g., wood, metal), suggest specific "
        "materials within the same category."
        "\n\nConsider the design brief for context (only where relevant), but "
        "don't explicitly mention it in the texture prompts."
        "\n\nFor each suggested material, provide a short, concrete explanation and a "
        "detailed texture map prompt suitable for a text-to-image generator."
    )
    return text


# ---------------------------------------------------------------------------
# Per-part prompt ideas (shown as chips when a part is selected)
# ---------------------------------------------------------------------------

PART_PROMPTS_SCHEMA = {
    "type": "object",
    "properties": {
        "material_prompts": {
            "type": "array",
            "items": {"type": "string"},
        },
        "color_prompts": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": ["material_prompts", "color_prompts"],
}


def suggest_part_prompts_prompt(object_name: str, part_name: str,
                                material_name: str | None = None) -> str:
    part = object_name if object_name == part_name else f"{object_name} {part_name}"
    text = (
        f'The user selected the "{part}" in their 3D scene.'
    )
    if material_name and material_name != "none":
        text += f' It is currently made of {material_name}.'
    text += (
        "\n\nWrite 3 short prompts the user could ask you to get MATERIAL "
        "suggestions for this part, and 3 short prompts to get COLOR/PALETTE "
        "suggestions for it. Make each prompt specific to this part and to the "
        "design brief (setting, style, durability needs). Phrase them as "
        "requests, e.g. \"Suggest weather-resistant materials for the chair seat\". "
        "Keep each under 12 words."
    )
    return text


# ---------------------------------------------------------------------------
# Proactive scene feedback (asynchronous, always grounded in the brief)
# ---------------------------------------------------------------------------

SUGGESTION_KINDS = ["material", "color", "finish", "other"]

SCENE_FEEDBACK_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "observations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "aspect": {"type": "string"},
                    "text": {"type": "string"},
                    "suggestions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "kind": {"type": "string",
                                         "enum": SUGGESTION_KINDS},
                            },
                            "required": ["name", "kind"],
                        },
                    },
                },
                "required": ["aspect", "text", "suggestions"],
            },
        },
    },
    "required": ["summary", "observations"],
}


def feedback_scene_prompt(scene_summary: str, has_image: bool = False,
                          web_context: str | None = None) -> str:
    text = (
        "Review the current state of the user's 3D interior design scene "
        "against the design brief.\n\nCurrent scene (object / part: material "
        "and finish):\n"
        f"{scene_summary}\n"
    )
    if has_image:
        text += (
            "\nA rendered image of the current scene is attached; base your "
            "feedback on what is actually visible (colors, materials, harmony) "
            "as well as the listing above.\n"
        )
    text += (
        "\nGive a 1-2 sentence overall summary, then 2-4 focused observations. "
        "Every observation must explicitly relate to the design brief (its "
        "style, colors, setting, durability, or budget). Start with how well "
        "the scene aligns with the brief. For each observation give up to 2 "
        "concrete suggestions (a material, color, or finish to try), each with "
        "a short name and its kind."
    )
    return with_web_context(text, web_context)


# ---------------------------------------------------------------------------
# Brainstorming
# ---------------------------------------------------------------------------

N_MATERIAL_SUGGESTION_PROMPTS = 5

MATERIAL_QUERIES_SCHEMA = {
    "type": "object",
    "properties": {
        "prompts": {
            "type": "array",
            "items": {"type": "string"},
        }
    },
    "required": ["prompts"],
}

MATERIALS_SUGGESTION_PROMPT = f'''Brainstorm prompts that a user can ask you to suggest materials or color palettes for the project in the design brief.
Base these prompts on criteria from the brief such as price, its interior design style,
environmental sustainability, durability, setting (e.g. outdoor, indoor, coastal, tropical), or local availability.
Make the prompts concise. Return {N_MATERIAL_SUGGESTION_PROMPTS} prompts.'''

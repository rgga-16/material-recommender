"""Prompt text and JSON-schema definitions for the local LLM service.

Ported (text-only; no image inputs) from the old models/llm/gpt3 module.
"""

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = '''You are an interior and furniture design expert with expert knowledge of materials. Your role is to:

1) Suggest materials and color palettes when asked, depending on the criteria to suggest them.
2) Provide feedback on materials when asked, depending on the criteria to provide feedback.

Keep your replies concise.'''


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


def suggest_materials_prompt(prompt: str, design_brief: str | None = None, n: int = 4) -> str:
    text = f"{prompt}\n\nSuggest {n} suitable materials."
    if design_brief:
        text += (
            f"\n\nConsider the following design brief for context "
            f"(only where relevant):\n{design_brief}"
        )
    text += (
        "\n\nReturn a short intro sentence and a list of materials, each with a name "
        "and a brief, concrete reason (1-2 sentences)."
    )
    return text


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


def suggest_color_palettes_prompt(prompt: str, design_brief: str | None = None) -> str:
    text = f"{prompt}. Suggest a few color palettes."
    if design_brief:
        text += (
            f"\n\nConsider the following design brief for context "
            f"(only where relevant):\n{design_brief}"
        )
    text += (
        "\n\nFor each palette, give a name, a brief description, and a list of "
        "hex color codes in the form #RRGGBB (e.g. #FFC300)."
    )
    return text


# ---------------------------------------------------------------------------
# Texture prompts / keywords (text-only: takes a material name instead of an image)
# ---------------------------------------------------------------------------

TEXTURE_KEYWORDS_SCHEMA = {
    "type": "object",
    "properties": {
        "keywords": {
            "type": "array",
            "items": {"type": "string"},
        }
    },
    "required": ["keywords"],
}


def brainstorm_prompt_keywords_prompt(material: str, design_brief: str | None = None) -> str:
    text = (
        f"I am using a text-to-image model to create an image of a {material} texture map "
        f"by typing in a text prompt. Brainstorm example keywords I can append to the text "
        f"prompt to make a more detailed and accurate image of a {material} texture map."
    )
    if design_brief:
        text += (
            f"\n\nI'm trying to make a texture map that aligns with the following design "
            f"brief:\n{design_brief}"
        )
    text += "\n\nReturn only the keywords."
    return text


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


def get_texture_prompts_prompt(prompt: str, n: int, design_brief: str | None = None) -> str:
    text = (
        f"Please make {n} varying text prompts that can be used with a text-to-image "
        f"generator to create detailed, flat, seamless texture map images."
    )
    if prompt:
        text += f"\n\nUse the following as guidance for the prompts:\n{prompt}"
    if design_brief:
        text += (
            f"\n\nConsider the following design brief for context, but don't explicitly "
            f"mention it in the texture prompts:\n{design_brief}"
        )
    text += "\n\nFor each prompt, also give a brief reason."
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


def get_materials_prompt(material_name: str, prompt: str, n: int,
                          design_brief: str | None = None) -> str:
    text = (
        f"Based on the material \"{material_name}\", please suggest {n} materials that "
        f"are similar to it"
    )
    if prompt:
        text += f" and that also address the following query: {prompt}"
    text += (
        ". If the material name is generic (e.g., wood, metal), suggest specific "
        "materials within the same category."
    )
    if design_brief:
        text += (
            f"\n\nConsider the following design brief for context "
            f"(only where relevant), but don't explicitly mention it in the texture "
            f"prompts:\n{design_brief}"
        )
    text += (
        "\n\nFor each suggested material, provide a short, concrete explanation and a "
        "detailed texture map prompt suitable for a text-to-image generator."
    )
    return text


# ---------------------------------------------------------------------------
# Material feedback
# ---------------------------------------------------------------------------

FEEDBACK_ASPECTS = ["durability", "maintenance", "sustainability", "assembly", "cost", "availability"]

FEEDBACK_SCHEMA = {
    "type": "object",
    "properties": {
        aspect: {
            "type": "object",
            "properties": {
                "feedback": {"type": "string"},
                "suggestions": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
            },
            "required": ["feedback", "suggestions"],
        }
        for aspect in FEEDBACK_ASPECTS
    },
    "required": FEEDBACK_ASPECTS,
}


def feedback_materials_prompt(material_name: str, object_name: str, part_name: str,
                               attached_parts=None, design_brief: str | None = None) -> str:
    if object_name == part_name:
        part_name = ""
    text = f"I have a {object_name} {part_name} made out of {material_name}. "

    if attached_parts:
        text += "Here is information on other parts it is attached to:\n"
        for attached_part in attached_parts:
            parent, part, mat = attached_part[0], attached_part[1], attached_part[2]
            if parent == part:
                text += f"It is attached to a {parent} made out of {mat}. "
            else:
                text += f"It is attached to a {parent} {part} made out of {mat}. "

    text += (
        f"\n\nBased on the information above, provide feedback on the material used, "
        f"for each of the following aspects: {', '.join(FEEDBACK_ASPECTS)}. "
        f"For each aspect, if the feedback is critical, provide up to 3 suggestions "
        f"(e.g. alternative materials, finishes, attachments) to improve it, as a list "
        f"of [name, type] pairs where type is one of: material, finish, attachment, other. "
        f"Consider the object the material is used on."
    )

    if design_brief:
        text += (
            f"\n\nConsider the following design brief for context "
            f"(only where relevant):\n{design_brief}"
        )

    return text


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

MATERIALS_SUGGESTION_PROMPT = f'''Brainstorm prompts that a user can ask you to suggest materials.
Base these prompts on criteria such as price, a specific interior design style
(e.g. Scandinavian, Contemporary), environmental sustainability, durability,
setting (e.g. outdoor, indoor, coastal, tropical), or local availability.
Make the prompts concise. Return {N_MATERIAL_SUGGESTION_PROMPTS} prompts.'''

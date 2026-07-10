"""Auto-style route: one LLM call assigns a coherent material + color to every
selectable part of the scene in one shot ("Style my scene").

POST /api/auto_style
    body: {"style": "industrial", "parts": [{"object": "sofa", "part": "frame"}, ...]}
    -> {"job_id": "<hex>"}

The job (run in the single-worker jobs executor, same as texture generation)
does the following:
    1. Scans the preset-material vocabulary (server.routes.presets._scan_preset_materials).
    2. Makes one llm.generate_json call: given the style + the part list + the
       preset vocabulary, the model returns one assignment per part, each
       either "source": "preset" (referencing a preset by name) or
       "source": "generate" (a short SD-Turbo texture prompt).
    3. Post-processes defensively (the local 1.5B model is small and will
       sometimes drop parts, invent preset names, or return malformed
       colors/numbers):
        - every requested part gets exactly one assignment (missing ones get
          a neutral-grey preset default);
        - "preset" assignments are resolved to the closest known preset name
          (case-insensitive substring match, else the first preset);
        - "generate" assignments call generate_and_save(...) to produce a
          real texture + normal/height maps, de-duplicating identical
          prompts so we only run SD-Turbo once per distinct prompt;
        - colors are validated as #RRGGBB (else replaced with a neutral
          grey) and roughness/metalness are clamped to [0, 1].
    4. Reports progress via jobs.set_progress as each part is finalized.

Registration (done by the main agent, not here):
    from server.routes import autostyle
    app.register_blueprint(autostyle.bp)
"""
import re

from flask import Blueprint, jsonify, request

from server.routes.presets import _scan_preset_materials
from server.routes.textures import generate_and_save
from server.services import jobs, llm

bp = Blueprint("autostyle", __name__)

_HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
_NEUTRAL_COLOR = "#C8C2B8"
_DEFAULT_ROUGHNESS = 0.6
_DEFAULT_METALNESS = 0.0

_ASSIGNMENT_SCHEMA = {
    "type": "object",
    "properties": {
        "assignments": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "object": {"type": "string"},
                    "part": {"type": "string"},
                    "source": {"type": "string", "enum": ["preset", "generate"]},
                    "material": {"type": "string"},
                    "prompt": {"type": "string"},
                    "color": {"type": "string"},
                    "roughness": {"type": "number"},
                    "metalness": {"type": "number"},
                },
                "required": ["object", "part", "source", "material", "color",
                             "roughness", "metalness"],
            },
        },
    },
    "required": ["assignments"],
}

_SYSTEM_PROMPT = (
    "You are an interior and furniture design expert with deep knowledge of "
    "materials, finishes, and color theory. Given a design style and a list "
    "of furniture parts, you assign a coherent, realistic material and color "
    "to every part so the whole scene reads as one cohesive style. Keep "
    "replies concise and always follow the requested JSON schema exactly."
)


def _build_prompt(style, parts, preset_names):
    parts_lines = "\n".join(f"- object: \"{p['object']}\", part: \"{p['part']}\"" for p in parts)
    preset_list = ", ".join(preset_names) if preset_names else "(none available)"
    return (
        f"Design style: \"{style}\"\n\n"
        f"Assign a material and color to each of the following parts so they "
        f"form one coherent {style} scene:\n{parts_lines}\n\n"
        f"Available preset materials (prefer these when a good fit exists):\n"
        f"{preset_list}\n\n"
        "For each part, return an assignment with:\n"
        "- \"object\" and \"part\": copied exactly from the part list above.\n"
        "- \"source\": \"preset\" if one of the available preset materials fits "
        "well, otherwise \"generate\".\n"
        "- \"material\": the preset name (if source is \"preset\") or a short, "
        "descriptive material name (if source is \"generate\"), e.g. \"brushed "
        "brass\" or \"raw oak wood\".\n"
        "- \"prompt\": only needed when source is \"generate\" — a short "
        "text-to-image prompt describing the material's texture, e.g. "
        "\"weathered raw oak wood grain\".\n"
        "- \"color\": a hex color code in the form #RRGGBB that fits the "
        f"{style} style and forms a coherent palette across all parts.\n"
        "- \"roughness\": a number from 0 (mirror-smooth) to 1 (fully matte).\n"
        "- \"metalness\": a number from 0 (non-metallic) to 1 (fully metallic).\n\n"
        "Give exactly one assignment per part listed above, in the same order. "
        "Return ONLY the JSON object matching the schema."
    )


def _clamp01(value, default):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return default
    if value != value:  # NaN
        return default
    return max(0.0, min(1.0, value))


def _valid_color(color):
    if isinstance(color, str) and _HEX_COLOR_RE.match(color.strip()):
        return color.strip()
    return None


def _resolve_preset(material_name, presets):
    """Case-insensitive substring match against known preset names; falls
    back to the first preset (alphabetical, via _scan_preset_materials's
    sorted scan) if nothing matches. Returns (resolved_name, maps_dict) or
    (None, None) if there are no presets at all."""
    if not presets:
        return None, None

    if material_name:
        needle = material_name.strip().lower()
        for name in presets:
            if needle == name.lower():
                return name, presets[name]
        for name in presets:
            if needle in name.lower() or name.lower() in needle:
                return name, presets[name]

    fallback_name = next(iter(presets))
    return fallback_name, presets[fallback_name]


def _default_assignment(obj, part, presets):
    """Neutral fallback for a part the model failed to assign."""
    preset_name, maps = _resolve_preset(None, presets)
    result = {
        "object": obj,
        "part": part,
        "material_name": preset_name or "Default",
        "diffuse": maps["diffuse"] if maps else None,
        "normal": maps["normal"] if maps else None,
        "height": maps["height"] if maps else None,
        "color": _NEUTRAL_COLOR,
        "roughness": _DEFAULT_ROUGHNESS,
        "metalness": _DEFAULT_METALNESS,
        "source": "preset" if maps else "generate",
    }
    return result


def _derive_map_paths(diffuse_path):
    """<base>_normal.png / <base>_height.png, matching maps.generate_normal_and_height."""
    base, _ext = diffuse_path.rsplit(".", 1) if "." in diffuse_path else (diffuse_path, "png")
    return f"{base}_normal.png", f"{base}_height.png"


def run_auto_style(style, parts, job_id=None):
    """Job body for POST /api/auto_style. Returns the job result payload."""
    presets = _scan_preset_materials()
    preset_names = list(presets.keys())

    if job_id:
        jobs.set_progress(job_id, 0.05, "Asking the design assistant for a style plan...")

    parsed = llm.generate_json(
        [{"role": "user", "content": _build_prompt(style, parts, preset_names)}],
        schema=_ASSIGNMENT_SCHEMA,
        system=_SYSTEM_PROMPT,
    )
    raw_assignments = parsed.get("assignments", []) if isinstance(parsed, dict) else []

    # Index raw assignments by (object, part), case-insensitively, so we can
    # match them back to the exact parts that were requested regardless of
    # whether the small model reproduced casing/whitespace exactly.
    by_key = {}
    for a in raw_assignments:
        if not isinstance(a, dict):
            continue
        obj = str(a.get("object", "")).strip()
        part = str(a.get("part", "")).strip()
        if not obj or not part:
            continue
        by_key[(obj.lower(), part.lower())] = a

    total = max(len(parts), 1)
    finalized = []
    generated_cache = {}  # prompt -> {"diffuse":..., "normal":..., "height":...}

    for i, requested in enumerate(parts):
        obj = requested["object"]
        part = requested["part"]
        raw = by_key.get((obj.strip().lower(), part.strip().lower()))

        if raw is None:
            finalized.append(_default_assignment(obj, part, presets))
            if job_id:
                jobs.set_progress(job_id, 0.1 + 0.85 * (i + 1) / total,
                                   f"Styling {obj} / {part}...")
            continue

        source = raw.get("source") if raw.get("source") in ("preset", "generate") else "preset"
        material_name = str(raw.get("material", "")).strip()
        color = _valid_color(raw.get("color")) or _NEUTRAL_COLOR
        roughness = _clamp01(raw.get("roughness"), _DEFAULT_ROUGHNESS)
        metalness = _clamp01(raw.get("metalness"), _DEFAULT_METALNESS)

        if source == "preset":
            resolved_name, maps = _resolve_preset(material_name, presets)
            if resolved_name is None:
                # No presets exist at all on disk; fall back to generating.
                source = "generate"
            else:
                finalized.append({
                    "object": obj,
                    "part": part,
                    "material_name": resolved_name,
                    "diffuse": maps["diffuse"],
                    "normal": maps["normal"],
                    "height": maps["height"],
                    "color": color,
                    "roughness": roughness,
                    "metalness": metalness,
                    "source": "preset",
                })
                if job_id:
                    jobs.set_progress(job_id, 0.1 + 0.85 * (i + 1) / total,
                                       f"Styling {obj} / {part}...")
                continue

        # source == "generate"
        texture_prompt = str(raw.get("prompt", "")).strip() or material_name or f"{style} material"
        full_prompt = f"{texture_prompt}, texture map, seamless"

        if full_prompt in generated_cache:
            gen_paths = generated_cache[full_prompt]
        else:
            if job_id:
                jobs.set_progress(job_id, 0.1 + 0.85 * i / total,
                                   f"Generating {material_name or texture_prompt} texture...")
            result = generate_and_save(full_prompt, 1, 512)
            diffuse_path = result["results"][0]["texture"]
            normal_path, height_path = _derive_map_paths(diffuse_path)
            gen_paths = {"diffuse": diffuse_path, "normal": normal_path, "height": height_path}
            generated_cache[full_prompt] = gen_paths

        finalized.append({
            "object": obj,
            "part": part,
            "material_name": material_name or texture_prompt,
            "diffuse": gen_paths["diffuse"],
            "normal": gen_paths["normal"],
            "height": gen_paths["height"],
            "color": color,
            "roughness": roughness,
            "metalness": metalness,
            "source": "generate",
        })
        if job_id:
            jobs.set_progress(job_id, 0.1 + 0.85 * (i + 1) / total,
                               f"Styling {obj} / {part}...")

    if job_id:
        jobs.set_progress(job_id, 1.0, "Done.")

    return {"style": style, "assignments": finalized}


@bp.route("/api/auto_style", methods=["POST"])
def auto_style_route():
    form_data = request.get_json()
    style = form_data.get("style", "")
    parts = form_data.get("parts", [])
    job_id = jobs.submit(run_auto_style, style, parts, pass_job_id=True)
    return jsonify({"job_id": job_id})

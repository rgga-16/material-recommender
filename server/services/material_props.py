"""Material intelligence: map a material name to sensible PBR settings.

Classification is a cheap keyword match first; unknown names fall back to a
one-shot LLM classification (cached). The class then indexes a static table
of finish presets (roughness/metalness/etc.) and a typical texture tiling
scale, which the client applies right after a texture is dropped on a part.
"""
import logging
import threading

log = logging.getLogger(__name__)

# Per material class: MeshStandardMaterial scalars + texture repeat ("scale").
# opacity < 1 implies a transparent material client-side.
MATERIAL_CLASSES = {
    "metal":    {"roughness": 0.25, "metalness": 0.9,  "opacity": 1.0,  "normalScale": 0.6, "scale": 2},
    "wood":     {"roughness": 0.55, "metalness": 0.0,  "opacity": 1.0,  "normalScale": 1.0, "scale": 4},
    "fabric":   {"roughness": 0.9,  "metalness": 0.0,  "opacity": 1.0,  "normalScale": 1.2, "scale": 8},
    "leather":  {"roughness": 0.5,  "metalness": 0.0,  "opacity": 1.0,  "normalScale": 1.0, "scale": 4},
    "glass":    {"roughness": 0.05, "metalness": 0.0,  "opacity": 0.35, "normalScale": 0.2, "scale": 1},
    "plastic":  {"roughness": 0.35, "metalness": 0.0,  "opacity": 1.0,  "normalScale": 0.5, "scale": 2},
    "stone":    {"roughness": 0.7,  "metalness": 0.0,  "opacity": 1.0,  "normalScale": 1.0, "scale": 3},
    "ceramic":  {"roughness": 0.15, "metalness": 0.0,  "opacity": 1.0,  "normalScale": 0.4, "scale": 3},
    "concrete": {"roughness": 0.85, "metalness": 0.0,  "opacity": 1.0,  "normalScale": 1.0, "scale": 2},
    "paint":    {"roughness": 0.5,  "metalness": 0.0,  "opacity": 1.0,  "normalScale": 0.3, "scale": 1},
    "rubber":   {"roughness": 0.95, "metalness": 0.0,  "opacity": 1.0,  "normalScale": 0.8, "scale": 3},
    "paper":    {"roughness": 0.8,  "metalness": 0.0,  "opacity": 1.0,  "normalScale": 0.5, "scale": 2},
    "other":    {"roughness": 0.6,  "metalness": 0.0,  "opacity": 1.0,  "normalScale": 1.0, "scale": 2},
}

_KEYWORDS = {
    "metal": ["metal", "steel", "iron", "aluminum", "aluminium", "chrome", "brass",
              "copper", "bronze", "gold", "silver", "titanium", "zinc", "tin",
              "pewter", "nickel", "wrought"],
    "wood": ["wood", "oak", "pine", "walnut", "teak", "mahogany", "birch", "maple",
             "cedar", "bamboo", "plywood", "timber", "cherry", "ash", "beech",
             "rattan", "wicker", "cork", "driftwood", "acacia"],
    "fabric": ["fabric", "textile", "cotton", "linen", "wool", "velvet", "denim",
               "canvas", "upholstery", "felt", "silk", "polyester", "tweed",
               "chenille", "jute", "hemp", "burlap", "fleece", "knit", "woven",
               "cushion", "mesh"],
    "leather": ["leather", "suede", "hide", "cowhide"],
    "glass": ["glass", "crystal", "mirror"],
    "plastic": ["plastic", "acrylic", "pvc", "vinyl", "polycarbonate", "resin",
                "nylon", "polypropylene", "laminate", "melamine", "fiberglass"],
    "stone": ["stone", "marble", "granite", "slate", "travertine", "limestone",
              "sandstone", "quartz", "onyx", "basalt", "terrazzo", "pebble",
              "rock", "cobble", "flagstone"],
    "ceramic": ["ceramic", "porcelain", "tile", "terracotta", "earthenware",
                "clay", "mosaic", "enamel"],
    "concrete": ["concrete", "cement", "brick", "plaster", "stucco", "mortar",
                 "asphalt"],
    "paint": ["paint", "painted", "lacquer", "matte finish", "gloss finish"],
    "rubber": ["rubber", "foam", "silicone", "neoprene"],
    "paper": ["paper", "cardboard", "wallpaper", "parchment"],
}

CLASS_SCHEMA = {
    "type": "object",
    "properties": {
        "material_class": {"type": "string", "enum": list(MATERIAL_CLASSES)},
    },
    "required": ["material_class"],
}

_llm_cache = {}
_llm_cache_lock = threading.Lock()


def classify(material_name: str) -> str:
    """Material class for a free-form material name; never raises."""
    name = (material_name or "").strip().lower()
    if not name:
        return "other"
    for cls, words in _KEYWORDS.items():
        if any(w in name for w in words):
            return cls
    with _llm_cache_lock:
        if name in _llm_cache:
            return _llm_cache[name]
    cls = _classify_llm(name)
    with _llm_cache_lock:
        _llm_cache[name] = cls
    return cls


def _classify_llm(name: str) -> str:
    from server.services import llm
    try:
        parsed = llm.generate_json(
            [{"role": "user", "content":
              f'Classify the material "{name}" into exactly one of these classes: '
              f'{", ".join(MATERIAL_CLASSES)}. Pick "other" only if nothing fits.'}],
            schema=CLASS_SCHEMA,
            temperature=0.0,
        )
        cls = parsed.get("material_class", "other")
        return cls if cls in MATERIAL_CLASSES else "other"
    except llm.LLMUnavailableError:
        return "other"
    except Exception:
        log.warning("LLM material classification failed for %r", name, exc_info=True)
        return "other"


def properties_for(material_name: str) -> dict:
    cls = classify(material_name)
    props = dict(MATERIAL_CLASSES[cls])
    scale = props.pop("scale")
    return {"material_class": cls, "properties": props,
            "scale": {"scaleX": scale, "scaleY": scale}}

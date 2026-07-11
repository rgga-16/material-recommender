"""Pure helper functions: filename sanitizing, autostyle output repair."""
import pytest

from server.routes.autostyle import _clamp01, _resolve_preset, _valid_color
from server.routes.textures import _clamp_count, safe_filename_stem


# --------------------------------------------------------------- textures

@pytest.mark.parametrize("text,expected_start", [
    ("weathered oak wood", "weathered_oak_wood"),
    ("wood, 4.5k style", "wood__4_5k_style"),   # dots removed: client splits on "."
    ("../../evil", "evil"),
    ("", "texture"),
    ("   ", "texture"),
])
def test_safe_filename_stem(text, expected_start):
    stem = safe_filename_stem(text)
    assert stem.startswith(expected_start)
    assert "." not in stem
    assert "/" not in stem and "\\" not in stem


def test_stem_length_capped():
    assert len(safe_filename_stem("x" * 500)) <= 80


@pytest.mark.parametrize("n,expected", [(3, 3), (0, 1), (99, 8), ("4", 4), (None, 1), ("junk", 1)])
def test_clamp_count(n, expected):
    assert _clamp_count(n) == expected


# --------------------------------------------------------------- autostyle

def test_clamp01():
    assert _clamp01(0.5, 0.6) == 0.5
    assert _clamp01(-1, 0.6) == 0.0
    assert _clamp01(2, 0.6) == 1.0
    assert _clamp01("nope", 0.6) == 0.6
    assert _clamp01(float("nan"), 0.6) == 0.6


def test_valid_color():
    assert _valid_color("#AABB01") == "#AABB01"
    assert _valid_color(" #aabb01 ") == "#aabb01"
    assert _valid_color("red") is None
    assert _valid_color(None) is None


def test_resolve_preset_matching():
    presets = {"Concrete01": {"d": 1}, "Wood05": {"d": 2}}
    name, maps = _resolve_preset("wood05", presets)
    assert name == "Wood05"
    name, _ = _resolve_preset("wood", presets)
    assert name == "Wood05"
    name, _ = _resolve_preset("granite", presets)  # no match -> first preset
    assert name == "Concrete01"
    assert _resolve_preset("anything", {}) == (None, None)

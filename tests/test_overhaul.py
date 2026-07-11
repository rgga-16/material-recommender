"""Overhaul features: design brief store/routes, material intelligence,
smart-suggest intent classification, prompt enrichment fallback, web search
resilience, and the new/removed assistant endpoints. No GPU, no Ollama, no
network — everything external is monkeypatched."""
import json
import time

import pytest

from server import create_app
from server.routes import assistant
from server.services import design_brief, llm, material_props, texture_gen, websearch


@pytest.fixture(scope="module")
def client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


@pytest.fixture
def brief_file(tmp_path, monkeypatch):
    path = tmp_path / "design_brief.json"
    monkeypatch.setattr(design_brief, "DESIGN_BRIEF_PATH", str(path))
    return path


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """Web search and the LLM never leave the process in these tests."""
    monkeypatch.setattr(websearch, "search", lambda q, max_results=None: [])
    monkeypatch.setattr(llm, "generate_json",
                        lambda *a, **k: (_ for _ in ()).throw(
                            llm.LLMUnavailableError(llm.UNAVAILABLE_MSG)))


# ------------------------------------------------------------- design brief

def test_brief_defaults_then_roundtrips(brief_file):
    assert "Poolside Patio" in design_brief.get_brief()
    design_brief.set_brief("A cozy cabin office")
    assert design_brief.get_brief() == "A cozy cabin office"
    assert brief_file.exists()


def test_brief_blank_falls_back_to_default(brief_file):
    design_brief.set_brief("   ")
    assert "Poolside Patio" in design_brief.get_brief()


def test_brief_routes(client, brief_file):
    resp = client.get("/design_brief")
    assert resp.status_code == 200
    assert resp.get_json()["brief"]

    resp = client.post("/design_brief", json={"brief": "Rooftop bar, art deco"})
    assert resp.status_code == 200
    assert client.get("/design_brief").get_json()["brief"] == "Rooftop bar, art deco"

    assert client.post("/design_brief", json={}).status_code == 400
    assert client.post("/design_brief", json={"brief": "   "}).status_code == 400


def test_brief_pdf_rejects_junk(client, brief_file):
    resp = client.post("/design_brief_pdf", data={
        "file": (b"not a pdf at all", "brief.pdf"),
    }, content_type="multipart/form-data")
    assert resp.status_code == 400
    resp = client.post("/design_brief_pdf", data={}, content_type="multipart/form-data")
    assert resp.status_code == 400


def test_app_config_exposes_feedback_pacing(client):
    data = client.get("/app_config").get_json()
    assert data["feedback_debounce_s"] > 0
    assert data["feedback_min_interval_s"] > 0


def test_system_prompt_embeds_brief():
    from server.services import prompts
    text = prompts.system_prompt("BRIEF-MARKER-123")
    assert "BRIEF-MARKER-123" in text
    assert prompts.system_prompt(None) == prompts.BASE_SYSTEM_PROMPT


# ------------------------------------------------------ material intelligence

@pytest.mark.parametrize("name,expected", [
    ("Brushed Steel", "metal"),
    ("weathered teak", "wood"),
    ("outdoor canvas fabric", "fabric"),
    ("frosted glass", "glass"),
    ("polished marble", "stone"),
    ("terracotta tile", "ceramic"),
])
def test_material_classification_keywords(name, expected):
    assert material_props.classify(name) == expected


def test_material_classification_unknown_falls_back_without_llm():
    # LLM is unavailable (autouse fixture) -> "other", never an exception.
    assert material_props.classify("zzgibberishzz") == "other"


def test_properties_for_shape():
    result = material_props.properties_for("chrome")
    assert result["material_class"] == "metal"
    assert result["properties"]["metalness"] > 0.5
    assert result["scale"]["scaleX"] == result["scale"]["scaleY"]
    assert set(result["properties"]) == {"roughness", "metalness", "opacity",
                                         "normalScale"}


def test_material_properties_route(client):
    resp = client.post("/material_properties", json={"material_name": "oak wood"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["material_class"] == "wood"
    assert data["properties"]["metalness"] == 0.0
    assert client.post("/material_properties", json={}).status_code == 400


# ------------------------------------------------------------- smart suggest

@pytest.mark.parametrize("prompt,expected", [
    ("Suggest colors for the sofa", "colors"),
    ("What palette suits a coastal patio?", "colors"),
    ("Suggest durable materials for the chair", "materials"),
    ("Suggest materials and a color palette for the table", "both"),
])
def test_intent_classification_keyword_fast_path(prompt, expected):
    # No LLM available; these must resolve via keywords alone.
    assert assistant._classify_intent(prompt) == expected


def test_intent_classification_llm_failure_defaults_to_materials():
    assert assistant._classify_intent("make it pop") == "materials"


def _wait_for_job(client, job_id, timeout=10.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        job = client.get(f"/jobs/{job_id}").get_json()
        if job["status"] in ("done", "error"):
            return job
        time.sleep(0.05)
    raise AssertionError("job did not finish in time")


def test_suggest_submits_job(client):
    resp = client.post("/suggest", json={"prompt": "colors for a coastal patio"})
    assert resp.status_code == 200
    job = _wait_for_job(client, resp.get_json()["job_id"])
    # LLM is down -> the job errors, but through the job system (no 500s).
    assert job["status"] == "error"


def test_feedback_scene_submits_job(client):
    resp = client.post("/feedback_scene", json={})
    assert resp.status_code == 200
    job = _wait_for_job(client, resp.get_json()["job_id"])
    assert job["status"] in ("done", "error")


def test_removed_endpoints_are_gone(client):
    # Removed POST routes: the static catch-all matches the path for GET only,
    # so POST yields 404 (no such path) or 405 (path exists, wrong method) —
    # either way the assistant endpoint is gone.
    for path in ("/suggest_colors", "/suggest_materials", "/feedback_materials",
                 "/brainstorm_prompt_keywords"):
        assert client.post(path, json={"prompt": "x"}).status_code in (404, 405)


def test_suggest_part_prompts_503_when_llm_down(client):
    resp = client.post("/suggest_part_prompts", json={
        "object_name": "chair", "part_name": "seat"})
    assert resp.status_code == 503


# -------------------------------------------------------- prompt enrichment

def test_enrich_prompt_falls_back_when_llm_down(brief_file):
    assert texture_gen.enrich_prompt("wood") == "wood"
    assert texture_gen.enrich_prompt("  ") == ""


def test_enrich_prompt_uses_and_caches_llm(monkeypatch, brief_file):
    calls = []

    def fake_generate_json(*args, **kwargs):
        calls.append(1)
        return {"prompt": "weathered oak planks, natural grain, satin varnish"}

    monkeypatch.setattr(llm, "generate_json", fake_generate_json)
    texture_gen._enrich_cache.clear()
    first = texture_gen.enrich_prompt("wood")
    assert "oak" in first and "wood" in first
    assert texture_gen.enrich_prompt("wood") == first
    assert len(calls) == 1  # cached


def test_enrich_prompt_prepends_material_when_missing(monkeypatch, brief_file):
    monkeypatch.setattr(llm, "generate_json",
                        lambda *a, **k: {"prompt": "shiny chrome surface"})
    texture_gen._enrich_cache.clear()
    assert texture_gen.enrich_prompt("brass").startswith("brass,")


# --------------------------------------------------------------- web search

def test_websearch_empty_query_is_empty():
    assert websearch.context_block("") == ("", "")


def test_websearch_context_block_formats_results(monkeypatch):
    monkeypatch.setattr(websearch, "search", lambda q, max_results=None: [
        {"title": "Teak guide", "snippet": "Teak is durable.", "url": "https://x.test/teak"},
    ])
    context, references = websearch.context_block("teak")
    assert "Teak is durable." in context
    assert "[Teak guide](https://x.test/teak)" in references

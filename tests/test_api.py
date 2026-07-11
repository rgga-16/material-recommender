"""Route-level tests via the Flask test client (no GPU, no Ollama)."""
import json

import pytest

from server import create_app
from server.services import jobs


@pytest.fixture(scope="module")
def client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_missing_json_body_is_400(client):
    resp = client.post("/generate_textures", data="not json", content_type="text/plain")
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_missing_fields_is_400(client):
    resp = client.post("/get_image", json={})
    assert resp.status_code == 400
    assert "image_data" in resp.get_json()["error"]


def test_path_traversal_is_403(client):
    resp = client.post("/get_image", json={"image_data": "../requirements.txt"})
    assert resp.status_code == 403


def test_transfer_texture_rejects_outside_paths(client):
    resp = client.post("/transfer_texture", json={
        "src_url": "C:/Windows/win.ini" ,
        "curr_textureparts_path": "gen_images/renderings/current/object_part_material.json",
    })
    assert resp.status_code == 403


def test_unknown_job_is_404(client):
    assert client.get("/jobs/deadbeef").status_code == 404
    assert client.get("/jobs/deadbeef/events").status_code == 404


def test_job_sse_stream_ends_with_done(client):
    job_id = jobs.submit(lambda: {"ok": True})
    resp = client.get(f"/jobs/{job_id}/events")
    assert resp.mimetype == "text/event-stream"
    events = [json.loads(line[6:]) for line in resp.get_data(as_text=True).splitlines()
              if line.startswith("data: ")]
    assert events
    assert events[-1]["status"] == "done"
    assert events[-1]["result"] == {"ok": True}


def test_autostyle_validates_body(client):
    resp = client.post("/api/auto_style", data="junk", content_type="application/json")
    assert resp.status_code == 400

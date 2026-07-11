"""server.services.jobs: lifecycle, progress, update waits, TTL eviction."""
import time

from server.services import jobs


def _wait_done(job_id, timeout=5.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        job = jobs.get(job_id)
        if job and job["status"] in ("done", "error"):
            return job
        time.sleep(0.01)
    raise AssertionError("job did not finish in time")


def test_job_success_result():
    job_id = jobs.submit(lambda: {"answer": 42})
    job = _wait_done(job_id)
    assert job["status"] == "done"
    assert job["result"] == {"answer": 42}
    assert job["progress"] == 1.0


def test_job_error_captured():
    def boom():
        raise ValueError("kaput")
    job_id = jobs.submit(boom)
    job = _wait_done(job_id)
    assert job["status"] == "error"
    assert "kaput" in job["error"]


def test_progress_reporting():
    def work(job_id=None):
        jobs.set_progress(job_id, 0.5, "halfway")
        return "ok"
    job_id = jobs.submit(work, pass_job_id=True)
    job = _wait_done(job_id)
    assert job["status"] == "done"
    assert job["message"] == "halfway"


def test_unknown_job():
    assert jobs.get("nope") is None
    job, version = jobs.wait_for_update("nope", -1, timeout=0.05)
    assert job is None


def test_wait_for_update_sees_terminal_state():
    job_id = jobs.submit(lambda: "done-result")
    _wait_done(job_id)
    job, version = jobs.wait_for_update(job_id, -1, timeout=1.0)
    assert job["status"] == "done"
    assert "_version" not in job  # private fields stay private


def test_ttl_eviction(monkeypatch):
    monkeypatch.setattr(jobs, "JOB_TTL_SECONDS", 0.0)
    job_id = jobs.submit(lambda: "bye")
    _wait_done(job_id)
    # Eviction is lazy: the next submit sweeps expired jobs.
    jobs.submit(lambda: "hi")
    deadline = time.monotonic() + 2.0
    while jobs.get(job_id) is not None and time.monotonic() < deadline:
        time.sleep(0.01)
        jobs.submit(lambda: "sweep")
    assert jobs.get(job_id) is None

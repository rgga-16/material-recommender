"""In-process background job system.

A single-worker ThreadPoolExecutor serializes all GPU-bound work (texture
generation, normal/height maps, auto-style), which doubles as the VRAM mutex
on small GPUs. Heavy routes submit a job and return its id immediately; the
frontend polls GET /jobs/<id>.
"""
import threading
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor

_executor = ThreadPoolExecutor(max_workers=1)
_jobs = {}
_lock = threading.Lock()


def submit(fn, *args, pass_job_id=False, **kwargs):
    """Run fn(*args, **kwargs) in the worker thread. Returns a job id.

    With pass_job_id=True, fn also receives job_id=<id> so it can report
    progress via set_progress().
    """
    job_id = uuid.uuid4().hex
    with _lock:
        _jobs[job_id] = {"status": "queued", "progress": 0.0, "message": None,
                         "result": None, "error": None}

    def _run():
        with _lock:
            _jobs[job_id]["status"] = "running"
        try:
            if pass_job_id:
                kwargs["job_id"] = job_id
            result = fn(*args, **kwargs)
            with _lock:
                _jobs[job_id].update(status="done", progress=1.0, result=result)
        except Exception as e:
            traceback.print_exc()
            with _lock:
                _jobs[job_id].update(status="error", error=str(e))

    _executor.submit(_run)
    return job_id


def set_progress(job_id, progress, message=None):
    with _lock:
        job = _jobs.get(job_id)
        if job is not None and job["status"] == "running":
            job["progress"] = float(progress)
            if message is not None:
                job["message"] = message


def get(job_id):
    """Return the job dict (status/progress/message/result/error) or None."""
    with _lock:
        job = _jobs.get(job_id)
        return dict(job) if job is not None else None

"""In-process background job system.

A single-worker ThreadPoolExecutor serializes all GPU-bound work (texture
generation, normal/height maps, auto-style), which doubles as the VRAM mutex
on small GPUs. Heavy routes submit a job and return its id immediately; the
frontend subscribes to GET /jobs/<id>/events (SSE) or polls GET /jobs/<id>.

Finished jobs are kept for JOB_TTL_SECONDS and then evicted (lazily, on the
next submit) so the registry can't grow without bound.
"""
import logging
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

from server.config import JOB_TTL_SECONDS

log = logging.getLogger(__name__)

_executor = ThreadPoolExecutor(max_workers=1)
_jobs = {}
# Guards _jobs; notified on every job update so SSE streams can push
# promptly instead of polling.
_cond = threading.Condition()

_PRIVATE_KEYS = ("_expires_at", "_version")


def _evict_expired_locked():
    now = time.monotonic()
    for job_id in [jid for jid, job in _jobs.items()
                   if job["_expires_at"] is not None and job["_expires_at"] < now]:
        del _jobs[job_id]


def _update_locked(job_id, **fields):
    job = _jobs.get(job_id)
    if job is None:
        return
    job.update(fields)
    job["_version"] += 1
    _cond.notify_all()


def submit(fn, *args, pass_job_id=False, **kwargs):
    """Run fn(*args, **kwargs) in the worker thread. Returns a job id.

    With pass_job_id=True, fn also receives job_id=<id> so it can report
    progress via set_progress().
    """
    job_id = uuid.uuid4().hex
    with _cond:
        _evict_expired_locked()
        _jobs[job_id] = {"status": "queued", "progress": 0.0, "message": None,
                         "result": None, "error": None,
                         "_expires_at": None, "_version": 0}

    def _run():
        with _cond:
            _update_locked(job_id, status="running")
        try:
            if pass_job_id:
                kwargs["job_id"] = job_id
            result = fn(*args, **kwargs)
            with _cond:
                _update_locked(job_id, status="done", progress=1.0, result=result,
                               _expires_at=time.monotonic() + JOB_TTL_SECONDS)
        except Exception as e:
            log.exception("job %s failed", job_id)
            with _cond:
                _update_locked(job_id, status="error", error=str(e),
                               _expires_at=time.monotonic() + JOB_TTL_SECONDS)

    _executor.submit(_run)
    return job_id


def set_progress(job_id, progress, message=None):
    with _cond:
        job = _jobs.get(job_id)
        if job is not None and job["status"] == "running":
            fields = {"progress": float(progress)}
            if message is not None:
                fields["message"] = message
            _update_locked(job_id, **fields)


def _public(job):
    return {k: v for k, v in job.items() if k not in _PRIVATE_KEYS}


def get(job_id):
    """Return the job dict (status/progress/message/result/error) or None."""
    with _cond:
        job = _jobs.get(job_id)
        return _public(job) if job is not None else None


def wait_for_update(job_id, last_version, timeout=25.0):
    """Block until the job changes past last_version, it finishes, or timeout.

    Returns (job_dict_or_None, version). Used by the SSE stream: each yield
    passes its version back in so no update is missed between yields.
    """
    deadline = time.monotonic() + timeout
    with _cond:
        while True:
            job = _jobs.get(job_id)
            if job is None:
                return None, last_version
            if job["_version"] != last_version or job["status"] in ("done", "error"):
                return _public(job), job["_version"]
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return _public(job), job["_version"]
            _cond.wait(remaining)

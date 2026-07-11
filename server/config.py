"""Central configuration.

Every tunable lives here (single source of truth) and can be overridden with
an environment variable of the same name, e.g. ``set APP_PORT=8080``.
"""
import os

# Repo root (parent of the server/ package)
CWD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATIC_IMDIR = os.path.join(CWD, "client", "public")
SERVER_IMDIR = os.path.join(STATIC_IMDIR, "gen_images")
SERVER_PRESET_IMDIR = os.path.join(STATIC_IMDIR, "preset_materials")
# Path prefix the browser uses to reach generated images (relative to client/public)
CLIENT_IMDIR = "gen_images"

DATA_DIR = os.path.join(CWD, "data")
MODELS_3D_DIR = os.path.join(DATA_DIR, "3d_models")
SCENES_DIR = os.path.join(DATA_DIR, "scenes")

# Bundled demo scene used to bootstrap the current scene on first launch
DEMO_SCENE = os.environ.get("DEMO_SCENE", "pool-side-small")


def _env_int(name, default):
    try:
        return int(os.environ[name])
    except (KeyError, ValueError):
        return default


def _env_float(name, default):
    try:
        return float(os.environ[name])
    except (KeyError, ValueError):
        return default


PORT = _env_int("APP_PORT", 2099)
HOST = os.environ.get("APP_HOST", "127.0.0.1")
# Waitress worker threads. SSE connections each hold a thread while a job is
# streaming, so keep a few spare beyond the expected number of open tabs.
SERVER_THREADS = _env_int("APP_SERVER_THREADS", 16)

# Local Ollama assistant
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:1.5b-instruct")
# Multimodal model used when a request carries scene screenshots. Pull with:
#   ollama pull qwen2.5vl:3b
OLLAMA_VISION_MODEL = os.environ.get("OLLAMA_VISION_MODEL", "qwen2.5vl:3b")
MAX_HISTORY_MESSAGES = _env_int("MAX_HISTORY_MESSAGES", 20)
# Idle chat sessions are dropped after this many seconds.
CHAT_SESSION_TTL_SECONDS = _env_int("CHAT_SESSION_TTL_SECONDS", 6 * 3600)

# Always-on DuckDuckGo web search for assistant prompts (best-effort; the
# assistant degrades to no-web-context when offline or the lookup fails).
WEBSEARCH_MAX_RESULTS = _env_int("WEBSEARCH_MAX_RESULTS", 5)
WEBSEARCH_TIMEOUT_S = _env_float("WEBSEARCH_TIMEOUT_S", 6.0)

# Proactive scene-feedback pacing, served to the client via GET /app_config.
# Debounce: quiet period after the last scene change before feedback runs.
# Min interval: floor between two feedback runs (also the idle-check cadence).
FEEDBACK_DEBOUNCE_S = _env_int("FEEDBACK_DEBOUNCE_S", 20)
FEEDBACK_MIN_INTERVAL_S = _env_int("FEEDBACK_MIN_INTERVAL_S", 180)

# Persisted design brief (editable in the UI, or set from an uploaded PDF)
DESIGN_BRIEF_PATH = os.path.join(DATA_DIR, "design_brief.json")

# Diffusion model (any diffusers text-to-image repo id; defaults assume a
# turbo-class model: 1-4 steps, guidance 0)
SD_MODEL_ID = os.environ.get("SD_MODEL_ID", "stabilityai/sd-turbo")
MIN_FREE_VRAM_GB = _env_float("MIN_FREE_VRAM_GB", 3.0)

# Finished/errored jobs are evicted this many seconds after completion.
JOB_TTL_SECONDS = _env_int("JOB_TTL_SECONDS", 3600)

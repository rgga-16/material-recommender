# Exploring Textures with Stable Diffusion

An AI-assisted interior/furniture texture design tool. Describe a material in
plain text and get a seamless texture (with matching normal and height maps)
applied to your 3D scene in seconds, chat with a local assistant for material
and color suggestions, or let auto-style texture an entire room in one click.
The app is fully local: texture generation runs on-device with SD-Turbo, the
chat assistant runs on a local Ollama model, and the scene is rendered live in
the browser with Three.js — no cloud APIs, no API keys, no network calls once
set up.

## Features

- **Text-to-texture** — generate seamless, tileable textures from a text
  prompt, with automatically derived normal and height maps.
- **Preset material library** — pick from a curated set of ready-made
  materials instead of generating from scratch.
- **AI chat assistant** — a local LLM that answers questions (streamed live)
  and suggests materials/colors for your scene.
- **Auto-style** — one click generates and applies a coherent material style
  across every object in the scene.
- **GLB/GLTF upload** — bring in your own rooms and furniture models
  (DRACO/meshopt/KTX2-compressed files supported).
- **Scene composition** — move, rotate, and scale objects in the scene.
- **High-res image export** — export a high-resolution render of the current
  view.
- **Save/load scenes** — snapshot the current scene and reload it later;
  scenes persist across restarts.
- **English/Japanese UI** — switchable interface language.

## Requirements

- Windows or Linux
- Python 3.10+
- NVIDIA GPU with 6GB+ VRAM recommended (CPU works but is slow)
- Node.js (to build the frontend)
- [Ollama](https://ollama.com) (for the chat assistant / auto-style)

## Setup

1. Create a virtual environment and install Python dependencies:

   ```bash
   python -m venv .venv
   # Windows: .venv\Scripts\activate
   # Linux/macOS: source .venv/bin/activate
   pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cu124
   pip install -r requirements.txt
   ```

2. Install [Ollama](https://ollama.com), then pull the assistant model:

   ```bash
   ollama pull qwen2.5:1.5b-instruct
   ```

3. Build the frontend:

   ```bash
   cd client
   npm install
   npm run build
   ```

4. Run the app:

   ```bash
   python app.py
   ```

   Then open http://localhost:2099. The server runs under waitress (a
   production WSGI server), not the Flask dev server.

The first texture generation request downloads the SD-Turbo weights
(~2.5GB) from Hugging Face; subsequent runs use the local cache.

## Configuration

Every tunable lives in `server/config.py` and can be overridden with an
environment variable of the same name:

| Variable | Default | Meaning |
|---|---|---|
| `APP_PORT` | `2099` | HTTP port |
| `APP_HOST` | `127.0.0.1` | Bind address |
| `APP_SERVER_THREADS` | `16` | waitress worker threads (SSE holds one per stream) |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama server |
| `OLLAMA_MODEL` | `qwen2.5:1.5b-instruct` | Assistant model |
| `SD_MODEL_ID` | `stabilityai/sd-turbo` | diffusers text-to-image repo id |
| `MIN_FREE_VRAM_GB` | `3.0` | Below this, the Ollama model is evicted before generating |
| `JOB_TTL_SECONDS` | `3600` | Finished jobs are evicted after this |
| `CHAT_SESSION_TTL_SECONDS` | `21600` | Idle chat sessions are dropped after this |
| `DEMO_SCENE` | `pool-side-small` | Bundled scene used on first launch |

## VRAM notes

- SD-Turbo peaks at roughly 3.4GB of VRAM during generation.
- The Ollama assistant model (qwen2.5:1.5b-instruct) uses roughly 1.5GB and
  is automatically evicted from VRAM when texture generation needs the
  headroom, so both fit comfortably in 6GB.

## Development

```bash
# Frontend dev server on :5173, proxying API calls to Flask on :2099
cd client && npm run dev

# Frontend checks
npm run lint          # ESLint (svelte plugin)
npm run format        # Prettier
npm test              # vitest unit tests
npm run check         # svelte-check

# Backend tests (no GPU/Ollama needed — heavy deps are imported lazily)
.venv/Scripts/python -m pytest tests -q
```

Both suites also run in CI (`.github/workflows/ci.yml`) on every push/PR.

## Scene format (v2)

Scenes are described by an `object_part_material.json` manifest shaped like:

```
{ "<object>": { "<part>": { ..., "model": "<path>", "node": "<mesh name>?" } } }
```

- Legacy scenes ship one `.gltf` file per part.
- Uploaded objects share a single `.glb`, and `node` names the specific mesh
  within it that a part refers to.
- Per-object placement (position/rotation/scale) is stored separately, in a
  sibling `transforms.json`.
- Every texture/model path in a manifest (and in API responses) is a public
  URL relative to `client/public` (e.g. `gen_images/renderings/current/x.png`),
  fetched by the browser as a plain static file.

Scenes persist across restarts: `renderings/current` and `renderings/saved`
are kept; only transient work dirs (generated candidates, suggestion
previews, action history) are cleared at startup.

## Architecture

- `app.py` — entry point (`python app.py`), serves the Flask app via waitress.
- `server/` — Flask backend package:
  - `config.py` — env-overridable paths and constants.
  - `paths.py` — public-URL ↔ disk-path translation; every client-supplied
    path is validated to stay inside `client/public`.
  - `http.py` — request-body validation helpers (missing fields → 400).
  - `routes/` — blueprints: `scenes`, `textures` (incl. `GET /jobs/<id>` and
    the `GET /jobs/<id>/events` SSE stream), `presets`, `assistant`
    (streamed chat via `POST /query_stream`; per-session history),
    `autostyle`, `static`.
  - `services/` — business logic: `texture_gen` (SD-Turbo, lazily imported),
    `maps` (normal/height maps via DeepBump with a cached ONNX session),
    `llm` (Ollama; per-session conversations), `jobs` (background job queue
    with progress + TTL eviction), `scene_store` (persistent scene storage).
- `client/` — Three.js/Svelte 5 + Vite frontend (`npm run build` inside
  `client/`; output lands in `client/public`, which doubles as Flask's
  static root). Rendering plumbing lives in `src/lib/three/`
  (scene setup with sRGB/ACES color management, shared loaders with
  DRACO/meshopt/KTX2 decoders, PBR material construction, selection logic);
  `src/components/ThreeDDisplay.svelte` wires it to the UI. Long-running
  work is followed over SSE (`src/lib/jobs.js`) with a polling fallback.
- `data/3d_models/` — bundled demo scene and model assets.
- `utils/DeepBump-7/` — vendored ONNX-based normal/height map generation
  (GPL-3.0; only the inference modules are used).
- `tests/` — backend test suite (pytest); frontend unit tests live next to
  the modules they cover (`client/src/**/*.test.js`).
- `research/` — user-study analysis scripts and outputs from the original
  PhD research (not used by the app).

## Research

This project originated as PhD research into AI-assisted texture and
material design workflows for interior/furniture visualization. Published
papers are in `papers/`; study analysis artifacts are in `research/`.

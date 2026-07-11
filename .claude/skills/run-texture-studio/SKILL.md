---
name: run-texture-studio
description: Run, start, launch, smoke-test, or screenshot Texture Studio (the AI texture design app) — start the Flask/waitress backend on :2099, drive the Svelte/Three.js UI headlessly, generate a texture end-to-end, run the backend/frontend test suites.
---

# Run Texture Studio

Local-first texture design app: Flask backend (`python app.py`, waitress on
:2099, SD-Turbo + Ollama) serving a built Svelte 5 + Three.js frontend from
`client/public/`. Drive it headlessly with the committed Playwright driver
(`.claude/skills/run-texture-studio/driver.mjs`) — it uses the system
Edge/Chrome via `playwright-core`, no browser download.

All paths below are relative to the repo root. Commands were verified on
Windows 11 in Git Bash (the Bash tool); use `.venv/Scripts/python` as shown.

## Prerequisites

- Python venv at `.venv` with `pip install -r requirements.txt`
  (plus torch per the header note in requirements.txt for CUDA).
- Node deps: `cd client && npm install` (includes `playwright-core`).
- Microsoft Edge or Chrome installed (the driver launches it headless).
- Ollama is optional — texture generation works without it; only the chat
  assistant/auto-style endpoints return 503 when it's down.

## Build

The built frontend is gitignored — **after a fresh checkout you must build
or the server serves 404s**:

```bash
cd client && npm run build
```

## Run (agent path)

Start the server in the background (first boot creates/persists the demo
scene under `client/public/gen_images/`):

```bash
.venv/Scripts/python app.py
# wait for it:
until curl -sf http://localhost:2099/ >/dev/null; do sleep 1; done
```

Then drive it:

```bash
# Load the app, wait for the 3D scene, screenshot, fail on console errors:
node .claude/skills/run-texture-studio/driver.mjs smoke

# Full user flow: type a prompt, click Generate, wait for the texture grid
# (SD-Turbo runs on the GPU; ~30-60s warm, minutes on first-ever run while
# ~2.5GB of weights download), screenshot, verify the images loaded:
node .claude/skills/run-texture-studio/driver.mjs generate "brushed copper"
```

Screenshots land in `.claude/skills/run-texture-studio/screenshots/`.
**Look at them** — a dark empty viewport means the GLTF scene didn't load.

API-level smoke without a browser (job queue + SSE):

```bash
JOB=$(curl -s -X POST http://localhost:2099/generate_textures \
  -H "Content-Type: application/json" \
  -d '{"texture_string":"oak wood","n":1,"imsize":512}' \
  | python -c "import sys,json;print(json.load(sys.stdin)['job_id'])")
curl -s -N --max-time 180 "http://localhost:2099/jobs/$JOB/events" | tail -3
# last event: {"status": "done", ..., "result": {"results": [{"texture": "gen_images/generated/..."}]}}
```

## Run (human path)

`python app.py` then open http://localhost:2099. For frontend work,
`cd client && npm run dev` serves on :5173 and proxies API calls to :2099.

## Test

```bash
.venv/Scripts/python -m pytest tests -q   # backend (39 tests, no GPU/Ollama needed)
cd client && npm test                     # vitest unit tests
cd client && npm run lint                 # ESLint
```

## Gotchas

- **No `chromium-cli` on this machine** — that's why the driver uses
  `playwright-core` with `channel: 'msedge'` (falls back to `chrome`).
- **Don't probe the WebGL canvas pixels** (`drawImage` from it outside the
  render loop reads blank — no `preserveDrawingBuffer`). Trust
  `page.screenshot()` instead.
- Console warnings mentioning `X4122` are ANGLE shader-precision noise on
  Windows — benign; the driver filters them.
- `client/public/` is Flask's static root AND Vite's build output. Never
  delete it wholesale; `npm run build` intentionally does not empty it.
- Scenes persist across restarts; transient dirs (`gen_images/generated`
  etc.) are cleared at server startup, so earlier generation results
  disappear from the UI after a restart by design.
- Port/model/Ollama settings are env vars (see README "Configuration");
  the server binds 127.0.0.1:2099 by default.

## Troubleshooting

- `index: 404` from `/` → frontend not built; run `cd client && npm run build`.
- Driver fails with `browserType.launch: Chromium distribution 'msedge' is not found`
  → no Edge; install Chrome or change the channel in driver.mjs.
- Generation job stays `queued` forever → another job holds the single GPU
  worker; jobs serialize by design.
- `503 Ollama is not running` from assistant endpoints → `ollama serve` +
  `ollama pull qwen2.5:1.5b-instruct` (texture generation is unaffected).

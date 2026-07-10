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
- **AI chat assistant** — a local LLM that answers questions and suggests
  materials/colors for your scene.
- **Auto-style** — one click generates and applies a coherent material style
  across every object in the scene.
- **GLB/GLTF upload** — bring in your own rooms and furniture models.
- **Scene composition** — move, rotate, and scale objects in the scene.
- **High-res image export** — export a high-resolution render of the current
  view.
- **Save/load scenes** — snapshot the current scene and reload it later.
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
   pip install torch --index-url https://download.pytorch.org/whl/cu124
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

   Then open http://localhost:2099.

The first texture generation request downloads the SD-Turbo weights
(~2.5GB) from Hugging Face; subsequent runs use the local cache.

## VRAM notes

- SD-Turbo peaks at roughly 3.4GB of VRAM during generation.
- The Ollama assistant model (qwen2.5:1.5b-instruct) uses roughly 1.5GB and
  is automatically evicted from VRAM when texture generation needs the
  headroom, so both fit comfortably in 6GB.

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

## Architecture

- `app.py` — entry point (`python app.py`), starts the Flask app on port 2099.
- `server/` — Flask backend package:
  - `config.py` — paths and constants (ports, directories, demo scene).
  - `routes/` — blueprints: `scenes`, `textures`, `presets`, `assistant`,
    `autostyle`, `static`.
  - `services/` — business logic: `texture_gen` (SD-Turbo), `maps` (normal/
    height map derivation via DeepBump), `llm`/`prompts` (Ollama assistant),
    `jobs` (background job queue), `scene_store` (scene persistence).
- `client/` — Three.js/Svelte 5 + Vite frontend (`npm run build` inside
  `client/`; `npm run dev` starts a Vite dev server on :5173 that proxies API
  and asset requests to the Flask server on :2099).
- `data/3d_models/` — bundled demo scene and model assets.
- `utils/DeepBump-7/` — local ONNX-based normal/height map generation from
  color textures.

## Research

This project originated as PhD research into AI-assisted texture and
material design workflows for interior/furniture visualization.

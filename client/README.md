# Texture Studio client

Svelte 5 (runes) + Vite frontend for the texture design tool. The Flask server
(`python app.py` at the repo root, port 2099) serves the **built** client from
`client/public/` and also writes generated images into `public/gen_images/` at
runtime.

## Commands

```bash
npm install
npm run build   # production build into public/ (never wipes gen_images/)
npm run dev     # Vite dev server on :5173, proxying API + assets to :2099
npm run check   # svelte-check
```

For `npm run dev`, start the Flask server first — the proxy in
`vite.config.js` forwards every API endpoint plus `gen_images/`,
`preset_materials/`, and `models/` to it.

## Layout

- `index.html` — Vite entry. `static/` — build-time assets (favicon), copied
  into `public/` on build. `public/` — build output **and** Flask's static
  root; `gen_images/` + `preset_materials/` inside it are server-owned, which
  is why `vite.config.js` sets `emptyOutDir: false` and `scripts/clean-assets.mjs`
  deletes only `public/assets/` + `public/index.html` before each build.
- `src/app.css` — design tokens (dark studio theme). All component styling
  goes through these custom properties.
- `src/lib/ui/` — the design-system primitives (Button, Slider, NumberInput,
  Card, Panel, Modal, …). Contracts documented in `../DESIGN.md`.
- `src/lib/` — shared modules: `registry.js` (imperative surfaces for the 3D
  viewport / inspector / generator), `history.js` (undo/redo), `toast.js`,
  `jobs.js` (async job polling), `i18n.js`, `utils.js`.
- `src/components/` — feature components. All are Svelte 5 runes-mode except
  `ThreeDDisplay.svelte` (imperative three.js, intentionally legacy syntax),
  `ActionsPanel.svelte`, and the `on:proceedToGenerate` event contract in
  `ChatBotModule/ChatBot.svelte`.
- `DESIGN.md` / `PORTING.md` (in `client/`) — design-system spec and the
  Svelte 3→5 porting rules used during the overhaul.

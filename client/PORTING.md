# Component port + restyle guide (Svelte 3 legacy → Svelte 5 runes)

Binding rules for every component port in this overhaul. Read together with
`DESIGN.md` (component contracts) and `src/app.css` (tokens).

## The one hard rule

**Fully port a file to runes or don't touch its script at all.** Mixing legacy
(`export let`, `$:`, `$$props`) and runes (`$props()`, `$state`, `$derived`,
`$effect`) in one file is a compile error. When you port, port everything.

## Syntax mapping

| Legacy | Runes |
|---|---|
| `export let x = 1;` | `let { x = 1 } = $props();` |
| `export let x;` + parent uses `bind:x` | `let { x = $bindable() } = $props();` |
| `export function f() {}` (instance export) | unchanged — still allowed and still callable via `bind:this` |
| `$: y = x * 2;` | `let y = $derived(x * 2);` |
| `$: { sideEffect(x); }` | `$effect(() => { sideEffect(x); });` |
| `let v; store.subscribe(x => v = x);` | delete — use `$store` directly in script/markup (works in runes mode; also updates live, which the manual subscribe-capture pattern sometimes didn't) |
| `on:click={h}` / `on:click\|preventDefault={h}` | `onclick={h}` / `onclick={(e) => { e.preventDefault(); h(e); }}` |
| `on:mousedown`, `on:mouseup`, `on:input`, … | `onmousedown`, `onmouseup`, `oninput`, … |
| `<slot />` | `{@render children?.()}` with `children` from `$props()` |
| `createEventDispatcher` | keep as-is if the parent still listens with `on:event` (deprecated but functional); do NOT half-convert an event contract across files |
| `<svelte:options accessors/>` | delete; expose exported functions instead |

Lifecycle: `onMount`/`onDestroy` unchanged. `let x = $state(...)` for any
variable that is reassigned and read by the template.

## Behavior preservation (non-negotiable)

- Keep every fetch endpoint, request body, and store read/write exactly as-is.
- Keep all EN/JA bilingual strings. Replace `let japanese; in_japanese.subscribe(...)`
  captures with direct `$in_japanese` usage (alias: `let japanese = $derived($in_japanese);`).
- Keep undo/redo semantics: live updates (slider drag / typing) update the 3D
  material only; the single history commit happens on release/blur — this is the
  Slider/NumberInput `onInput` vs `onCommit` split (see DESIGN.md).
- Keep exported instance functions that other files call (grep before removing).

## Restyle rules

- Replace ALL `w3-*` classes, inline `style="..."` attributes, and hardcoded
  colors/borders with token-based scoped styles and the primitives in
  `src/lib/ui/` (Button, IconButton, Field, TextInput, TextArea, Select, Slider,
  NumberInput, Switch, Card, Panel, PanelSection, Tabs, Modal, Spinner, Tooltip).
- Replace `<img src="./logos/*.svg">` icons with `@lucide/svelte` per-icon
  imports (`import X from '@lucide/svelte/icons/<kebab-name>'`, `size={16}`,
  `strokeWidth={1.75}`).
- Replace the compat shims: `svelte-loading-spinners` Circle → `lib/ui/Spinner.svelte`;
  `svelte-number-spinner` → `lib/ui/NumberInput.svelte`; `svelte-range-slider-pips`
  → `lib/ui/Slider.svelte` (values are plain numbers now, not one-element arrays).
- Layout density: compact, quiet, precise (dark studio tool). Section headings
  `--text-sm` 600 weight, body `--text-base`. Use `--sp-*` spacing only.
- Empty/loading states: centered `--text-muted` message; Spinner for loading.

## Verification

Do NOT run `npm run build`, `npm install`, or any git command (the orchestrator
runs the build gate — parallel builds collide). After editing, re-read your diff
and check: no `$:`/`export let` left in ported files, no `w3-` classes, no
`style="` inline attributes, no `./logos/` references, no hardcoded hex colors.

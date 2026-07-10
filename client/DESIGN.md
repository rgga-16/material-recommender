# Texture Studio — Design System Spec

Single source of truth for the UI overhaul. All primitives live in `src/lib/ui/`,
one component per file. **Style exclusively with the CSS custom properties defined
in `src/app.css`** (never hardcode colors/sizes). Look and feel: dark studio
design tool (Blender / Figma dark) — compact, quiet, precise.

## Rules for every primitive

- **Svelte 5 runes mode only**: `$props()`, `$state`, `$derived`, `$bindable`,
  event *attributes* (`onclick`), snippet children (`{@render children?.()}`).
  Never `export let`, `$:`, `on:click`, `createEventDispatcher`, or slots.
- Consumers may still be legacy-syntax components — that's fine (interop is
  automatic). Primitives must accept plain callback props (`onclick`, `onInput`,
  `onCommit`) so both worlds can use them.
- Spread `{...rest}` onto the root interactive element so `title`, `id`,
  `aria-*`, `style` pass through.
- Scoped `<style>` blocks, tokens only. No global styles. No external CSS deps.
- Keyboard + a11y: focusable controls get `:focus-visible` ring automatically
  (global style); use real `<button>`/`<input>`/`<select>` elements.
- Transitions: 120ms ease on background/border/color only.

## Control metrics (match these across primitives)

- Control height: **28px** (md), **24px** (sm). Font `var(--text-base)` /
  `var(--text-sm)`.
- Padding: horizontal `var(--sp-3)` (md), `var(--sp-2)` (sm).
- Radius: `var(--radius-md)` for controls, `var(--radius-lg)` for cards/panels/modals.
- Inputs: background `var(--bg-inset)`, border `1px solid var(--border-subtle)`,
  hover border `var(--border-strong)`, focus border `var(--accent)`.

## Component contracts (props → behavior)

### Button.svelte
`variant` ('primary'|'secondary'|'ghost'|'danger', default 'secondary'), `size`
('sm'|'md', default 'md'), `disabled`, `loading` (shows inline spinner, disables),
`fullWidth`, `onclick`, `children`, `...rest`.
- primary: `--accent` bg, `--text-on-accent`; hover `--accent-hover`.
- secondary: `--bg-elevated` bg, `1px solid var(--border-strong)`; hover `--bg-hover`.
- ghost: transparent; hover `--bg-hover`.
- danger: transparent w/ `--danger` text + border; hover: danger bg at 12% alpha.

### IconButton.svelte
`label` (required — becomes `aria-label` and `title`), `size` ('sm' 24px | 'md' 28px
square), `active` (bool → `--accent-muted` bg + `--accent` color), `disabled`,
`onclick`, `children` (the icon), `...rest`. Ghost look: transparent, hover `--bg-hover`,
radius `--radius-md`, color `--text-secondary` (hover `--text-primary`).

### Spinner.svelte
`size` (px number, default 20). Conic/ring spinner in `currentColor` (defaults to
`--accent` via `color`), respects reduced motion. No text.

### Tooltip.svelte
Wrapper: `text`, `position` ('top'|'bottom'|'left'|'right', default 'top'),
`children`. CSS-only (opacity/visibility on hover/focus-within, 300ms delay),
`--bg-elevated` bg, `--shadow-overlay`, `--text-xs`, never captures pointer events.

### Tabs.svelte
`tabs`: `[{ id, label, icon? (snippet) }]`, `active` (id), `onSelect(id)`.
Horizontal underline style: transparent bg, `--text-secondary` labels; active tab
`--text-primary` + 2px `--accent` underline; hover `--text-primary`. Height 32px,
`--text-sm`, gap `--sp-4`. Container gets `border-bottom: 1px solid var(--border-subtle)`.

### Slider.svelte
`value` ($bindable number), `min`, `max`, `step`, `disabled`, `onInput(value)`
(every change while dragging), `onCommit(value)` (pointer release / keyup /
change), `showValue` (default true → right-aligned numeric readout, `--text-xs`,
`--text-secondary`, min-width 2.5em). Custom-styled native `<input type=range>`:
4px track `--border-strong` with a filled portion in `--accent`
(background gradient trick), 12px round thumb `--text-primary` border `--accent`.

### NumberInput.svelte
`value` ($bindable), `min`, `max`, `step`, `decimals` (display rounding),
`unit` (optional suffix text), `disabled`, `onInput(value)` (live while typing,
only when parse succeeds), `onCommit(value)` (blur/Enter, clamped). Compact:
width 72px + optional unit label. Hide native spin buttons; ArrowUp/Down = ±step
(fires onInput). Clamp to [min,max] on commit.

### Switch.svelte
`checked` ($bindable), `disabled`, `onchange(checked)`, `label` (optional inline
right-side text). 32×18 pill, `--bg-active` off / `--accent` on, 14px knob.

### Field.svelte
Layout wrapper: `label`, `hint` (optional, `--text-xs` `--text-muted`),
`row` (bool: label left 96px fixed + control right; default stacked), `children`.
Labels: `--text-xs`, `--text-secondary`, 500 weight, `margin-bottom: var(--sp-1)`.

### TextInput.svelte / TextArea.svelte
`value` ($bindable), `placeholder`, `disabled`, `onEnter(value)` (TextInput only),
`oninput` passthrough, `...rest`. Input metrics above; TextArea `min-height: 72px`,
`resize: vertical`.

### Select.svelte
`value` ($bindable), `options`: `[{ value, label }]`, `disabled`, `onchange(value)`,
`...rest`. Native `<select>` styled like TextInput with a custom chevron
(inline SVG data-URI background).

### Card.svelte
Thumbnail card for textures/presets/scenes. `image` (url, optional), `label`
(optional caption), `selected` (bool → 2px `--accent` ring), `onclick`,
`ondblclick`, `size` (px width, default 96), `aspect` (default '1/1'),
`actions` (snippet, optional → absolutely-positioned overlay bar at bottom,
visible on hover/focus-within, `rgba(0,0,0,.55)` bg), `children` (optional body
below image), `...rest`. `--bg-elevated` bg, `--radius-lg`, border `--border-subtle`,
hover: border `--border-strong` + translateY(-1px). Image `object-fit: cover`.
If no image: render a `--bg-inset` placeholder block.

### Panel.svelte
`title` (optional header, `--text-sm` 600 weight), `padded` (default true),
`children`. `--bg-panel` bg, `1px solid var(--border-subtle)` border,
`--radius-lg`. Fills height (flex column; content scrolls).

### PanelSection.svelte
Collapsible section for inspector stacks. `title`, `open` ($bindable, default
true), `children`, `actions` (snippet, right side of header). Header: 32px row,
chevron (CSS triangle or inline SVG) rotating 90°, `--text-sm` 600,
`--text-secondary` hover `--text-primary`; `border-bottom: 1px solid
var(--border-subtle)`. Body padding `var(--sp-3)`.

### Modal.svelte
`open` ($bindable), `title`, `width` (default 560px), `onClose`, `children`,
`footer` (snippet, optional). Fixed backdrop `rgba(0,0,0,.55)` + `backdrop-filter:
blur(2px)`; panel `--bg-elevated`, `--radius-lg`, `--shadow-modal`, header with
title + X IconButton; Escape and backdrop click call `onClose`. Body scrolls
(`max-height: 70vh`). Render nothing when `!open`.

### Toast (restyle existing `src/components/Toast.svelte`)
Keep store contract (`toasts` array of `{id, message, type}`). Restyle: fixed
top-right stack, `--bg-elevated` bg, `--radius-md`, `--shadow-overlay`, 3px left
border in semantic color (info→`--accent`, success→`--success`, error→`--danger`),
`--text-sm`, slide/fade in.

## Icons

`@lucide/svelte` per-icon imports, e.g.
`import Sparkles from '@lucide/svelte/icons/sparkles'`, rendered as
`<Sparkles size={16} strokeWidth={1.75} />`. Sizes: 16 inside controls, 20 in the
icon rail. Never `<img src="./logos/...">` in new code.

## Reference usage

```svelte
<Button variant="primary" onclick={generate} loading={busy}>Generate</Button>
<Field label="Roughness" row>
  <Slider bind:value={roughness} min={0} max={1} step={0.1}
    onInput={preview} onCommit={commit} />
</Field>
<Card image={tex.url} label={tex.name} selected={sel === tex.id}
  onclick={() => (sel = tex.id)}>
  {#snippet actions()}<Button size="sm" onclick={apply}>Apply</Button>{/snippet}
</Card>
```

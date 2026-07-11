<script>
  // Per-part inspector editor (runes mode). Edits write to the live three.js
  // material immediately (onInput) and commit one undo/redo history entry on
  // release/blur (onCommit) via changeProperty().
  import DynamicImage from "./DynamicImage.svelte";
  import EditableTextbox from "./EditableTextbox.svelte";

  import Slider from "../lib/ui/Slider.svelte";
  import NumberInput from "../lib/ui/NumberInput.svelte";
  import Button from "../lib/ui/Button.svelte";
  import Field from "../lib/ui/Field.svelte";

  import Plus from "@lucide/svelte/icons/plus";
  import Ban from "@lucide/svelte/icons/ban";
  import ChevronDown from "@lucide/svelte/icons/chevron-down";
  import Download from "@lucide/svelte/icons/download";
  import Lightbulb from "@lucide/svelte/icons/lightbulb";

  import { in_japanese, selected_objs_and_parts } from "../stores.js";
  import { translate } from "../lib/i18n.js";
  import { addToHistory } from "../lib/history.js";
  import { postJson } from "../lib/api.js";
  import { saved_color_palettes } from "../stores.js";
  import { chatbot_input_message } from "../stores.js";
  import { actions_panel_tab } from "../stores.js";
  import { use_chatgpt } from "../stores.js";
  import { get } from "svelte/store";
  import { onMount, untrack } from "svelte";

  import { curr_texture_parts } from "../stores.js";

  let { part_parent_name, part_name, index } = $props();

  let japanese = $derived($in_japanese);

  // Snapshot the manifest entry once at creation (matches legacy semantics:
  // the editor re-mounts whenever the selection changes).
  const entry = get(curr_texture_parts)[part_parent_name][part_name];

  let material_name = $state(entry["mat_name"] ?? "None");
  let material_url = $state(entry["mat_image_texture"] ?? "None");
  let material_color = $state(entry["color"] ?? "#FFFFFF");
  let opacity = $state(entry["opacity"] ?? 1.0);
  let roughness = $state(entry["roughness"] ?? 0.5);
  let metalness = $state(entry["metalness"] ?? 0.0);
  let normalScale = $state(entry["normalScale"] ?? 1.0);
  let translationX = $state(entry["offsetX"] ?? 0);
  let translationY = $state(entry["offsetY"] ?? 0);
  let rotation = $state(entry["rotation"] ?? 0);
  let scaleX = $state(entry["scaleX"] ?? 1);
  let scaleY = $state(entry["scaleY"] ?? 1);
  let scale = $state((entry["scaleX"] ?? 1) === (entry["scaleY"] ?? 1) ? (entry["scaleX"] ?? 1) : 1);

  let palettes = $state(get(saved_color_palettes));
  let selected_palette_idx = $state(0);
  let selected_swatch_idx = $state(undefined);
  const no_color = { name: "No Color", code: "#FFFFFF" };
  let palette_dropdown_open = $state(false);

  let activeTab = $state("adjust-finish");

  let image = $state(null);
  export function updateImage() {
    image?.getImage();
  }

  /** Download this part's albedo + normal/height/AO maps as one zip. */
  function downloadTextureSet() {
    window.location.href = "/export_texture_set?texture=" + encodeURIComponent(material_url);
  }

  // Re-sync editor state when a manifest VALUE changes (texture drag, undo/
  // redo, auto-style). The store also fires with unchanged values (e.g. the
  // material-name binding writes it back on re-render, including mid-drag,
  // when the manifest still holds the pre-commit value) — so each control only
  // syncs when the manifest value itself changed since the last run, and the
  // body is untracked so the store is the effect's only dependency.
  const prev_manifest = { ...entry };
  const SYNCED_PROPS = [
    ["opacity", (v) => (opacity = v)],
    ["roughness", (v) => (roughness = v)],
    ["metalness", (v) => (metalness = v)],
    ["normalScale", (v) => (normalScale = v)],
    ["offsetX", (v) => (translationX = v)],
    ["offsetY", (v) => (translationY = v)],
    ["rotation", (v) => (rotation = v)],
    ["scaleX", (v) => (scaleX = v)],
    ["scaleY", (v) => (scaleY = v)],
  ];
  $effect(() => {
    const parts = $curr_texture_parts;
    const current = parts?.[part_parent_name]?.[part_name];
    if (!current) return;
    untrack(() => {
      if (current["mat_image_texture"] && current["mat_image_texture"] !== material_url) {
        material_url = current["mat_image_texture"];
        material_name = current["mat_name"] ?? material_name;
      }
      for (const [prop, assign] of SYNCED_PROPS) {
        if (prop in current && current[prop] !== prev_manifest[prop]) {
          prev_manifest[prop] = current[prop];
          assign(current[prop]);
        }
      }
    });
  });

  // ------------------------------------------------- live material updates

  export function updateOpacity(v) {
    selected_objs_and_parts.update((value) => {
      value[index].mesh.material.transparent = true;
      value[index].mesh.material.opacity = v;
      return value;
    });
  }

  export function updateRoughness(v) {
    selected_objs_and_parts.update((value) => {
      value[index].mesh.material.roughness = v;
      return value;
    });
  }

  export function updateMetalness(v) {
    selected_objs_and_parts.update((value) => {
      value[index].mesh.material.metalness = v;
      return value;
    });
  }

  export function updateNormalScale(v) {
    selected_objs_and_parts.update((value) => {
      value[index].mesh.material.normalScale.x = v;
      value[index].mesh.material.normalScale.y = v;
      return value;
    });
  }

  export function updateDisplacementScale(v) {
    selected_objs_and_parts.update((value) => {
      value[index].mesh.material.displacementScale = v;
      return value;
    });
  }

  const ALL_MAPS = [
    "map", "normalMap", "aoMap", "alphaMap", "emissiveMap", "lightMap",
    "metalnessMap", "roughnessMap", "displacementMap", "bumpMap", "envMap",
  ];

  function forEachMap(fn) {
    selected_objs_and_parts.update((value) => {
      const material = value[index].mesh.material;
      for (const key of ALL_MAPS) {
        if (material[key]) fn(material[key]);
      }
      return value;
    });
  }

  function degreeToRadians(degrees) {
    return degrees * (Math.PI / 180);
  }

  export function updateTextureMapOffset(x_or_y, val) {
    forEachMap((map) => (map.offset[x_or_y] = val));
  }

  export function updateTextureMapScale(x_or_y, val) {
    forEachMap((map) => (map.repeat[x_or_y] = val));
  }

  export function updateTextureMapOrientation(rot) {
    forEachMap((map) => (map.rotation = degreeToRadians(rot)));
  }

  // -------------------------------------------------------- history commit

  export function changeProperty(property, new_value, old_value = 0) {
    const parts = get(curr_texture_parts);
    if (parts[part_parent_name][part_name][property]) {
      old_value = parts[part_parent_name][part_name][property];
    }
    curr_texture_parts.update((value) => {
      value[part_parent_name][part_name][property] = new_value;
      return value;
    });
    addToHistory("Change " + property, part_parent_name, part_name, [property], [old_value], [new_value]);
  }

  // ----------------------------------------------------------- color logic

  function addNewColorPalette() {
    palettes.push({
      name: "New Palette",
      palette: ["#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF"],
    });
    palettes = palettes;
    saved_color_palettes.set(palettes);
  }

  function updateColor() {
    const color = palettes[selected_palette_idx]["palette"][selected_swatch_idx];
    const hexNumber = parseInt(color.substring(1), 16);
    selected_objs_and_parts.update((value) => {
      value[index].mesh.material.color.setHex(hexNumber);
      value[index].mesh.material.color_hex = hexNumber;
      return value;
    });
  }

  function commitColor() {
    updateColor();
    changeProperty("color", palettes[selected_palette_idx]["palette"][selected_swatch_idx], "#FFFFFF");
  }

  // ------------------------------------------------------------- assistant

  function suggestSimilarMaterials() {
    const target = part_parent_name === part_name ? part_parent_name : part_parent_name + " " + part_name;
    const query = "Can you suggest similar materials to " + material_name + " for a " + target + "?";
    actions_panel_tab.set("chatbot");
    chatbot_input_message.set(query);
  }

  // Prompt ideas for this part: instant template chips, refreshed by the
  // brief-aware assistant in the background.
  const part_label = part_parent_name === part_name
    ? part_parent_name
    : `${part_parent_name} ${part_name}`;

  let material_chips = $state([
    `Suggest materials for the ${part_label}`,
    `Suggest durable, low-maintenance materials for the ${part_label}`,
  ]);
  let color_chips = $state([
    `Suggest colors for the ${part_label}`,
    `Suggest a color palette that suits the ${part_label}`,
  ]);
  let is_refreshing_chips = $state(false);

  async function refreshPromptChips() {
    is_refreshing_chips = true;
    try {
      const data = await postJson("/suggest_part_prompts", {
        object_name: part_parent_name,
        part_name: part_name,
        material_name: material_name,
      });
      let mats = (data["material_prompts"] || []).filter(Boolean);
      let cols = (data["color_prompts"] || []).filter(Boolean);
      if (japanese) {
        mats = await Promise.all(mats.map((p) => translate("EN", "JA", p)));
        cols = await Promise.all(cols.map((p) => translate("EN", "JA", p)));
      }
      if (mats.length > 0) material_chips = mats;
      if (cols.length > 0) color_chips = cols;
    } catch (error) {
      // Template chips remain as the fallback.
      console.warn("prompt ideas unavailable", error);
    } finally {
      is_refreshing_chips = false;
    }
  }

  function useChip(text) {
    chatbot_input_message.set(text);
    actions_panel_tab.set("chatbot");
  }

  onMount(() => {
    if (get(use_chatgpt)) refreshPromptChips();
  });

  onMount(() => {
    // Seed a "Custom" palette from this part's current color.
    if (material_color) {
      for (let i = 0; i < palettes.length; i++) {
        if (palettes[i]["name"] === "Custom") {
          palettes.splice(i, 1);
        }
      }
      palettes.unshift({
        name: "Custom",
        palette: [material_color, "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF"],
      });
      palettes = palettes;
      saved_color_palettes.set(palettes);
      selected_palette_idx = 0;
      selected_swatch_idx = 0;
    }
  });

  const tabs = [
    { id: "adjust-finish", en: "Finish", ja: "仕上げ" },
    { id: "adjust-texture-map", en: "Texture", ja: "テクスチャ" },
    { id: "adjust-color", en: "Color", ja: "カラー" },
  ];
</script>

<div class="part-editor">
  <!-- header -->
  <div class="part-header">
    <div class="preview">
      <DynamicImage bind:this={image} bind:imagepath={material_url} alt={material_name} size="120px" />
    </div>
    <div class="part-meta">
      <div class="part-title">
        {#if part_parent_name === part_name}
          {part_name}
        {:else}
          <span class="parent">{part_parent_name}</span>
          <span class="sep">/</span>
          {part_name}
        {/if}
      </div>
      <div class="meta-row">
        <span class="meta-label">{japanese ? "素材" : "Material"}</span>
        <EditableTextbox bind:text={$curr_texture_parts[part_parent_name][part_name]["mat_name"]} />
      </div>
      <div class="meta-row">
        <span class="meta-label">{japanese ? "カラー" : "Color"}</span>
        <span class="color-chip" style="background-color: {$curr_texture_parts[part_parent_name][part_name]['color'] ?? '#FFFFFF'};"></span>
        <span class="color-code">{$curr_texture_parts[part_parent_name][part_name]["color"] ?? "none"}</span>
      </div>
      {#if material_url && material_name && material_name !== "none" && material_name !== "None"}
        <div class="meta-row">
          <Button size="sm" variant="secondary" onclick={downloadTextureSet}>
            <Download size={13} strokeWidth={1.75} />
            {japanese ? "テクスチャ一式をDL" : "Download texture set"}
          </Button>
        </div>
      {/if}
      {#if $use_chatgpt}
        <div class="assistant-actions">
          <Button size="sm" variant="secondary" onclick={suggestSimilarMaterials}>
            {japanese ? "類似素材の提案" : "Suggest similar"}
          </Button>
        </div>
      {/if}
    </div>
  </div>

  <!-- prompt ideas -->
  {#if $use_chatgpt}
    <div class="prompt-ideas">
      <div class="ideas-label">
        <Lightbulb size={13} strokeWidth={1.75} />
        {japanese ? "プロンプトのアイデア" : "Prompt ideas"}
        {#if is_refreshing_chips}
          <span class="ideas-refreshing">{japanese ? "更新中..." : "refreshing..."}</span>
        {/if}
      </div>
      <div class="idea-chips">
        {#each material_chips as chip (chip)}
          <button class="idea-chip material" onclick={() => useChip(chip)}>{chip}</button>
        {/each}
        {#each color_chips as chip (chip)}
          <button class="idea-chip color" onclick={() => useChip(chip)}>{chip}</button>
        {/each}
      </div>
    </div>
  {/if}

  <!-- tabs -->
  <div class="editor-tabs" role="tablist">
    {#each tabs as tab (tab.id)}
      <button
        class="editor-tab"
        class:active={activeTab === tab.id}
        role="tab"
        aria-selected={activeTab === tab.id}
        onclick={() => (activeTab = tab.id)}
      >
        {japanese ? tab.ja : tab.en}
      </button>
    {/each}
  </div>

  <!-- finish -->
  {#if activeTab === "adjust-finish"}
    <div class="tab-body">
      <Field label={japanese ? "透明度" : "Opacity"}>
        <Slider bind:value={opacity} min={0} max={1} step={0.1}
          onInput={(v) => updateOpacity(v)}
          onCommit={(v) => changeProperty("opacity", v, 1.0)} />
      </Field>
      <Field label={japanese ? "光沢" : "Roughness"}>
        <Slider bind:value={roughness} min={0} max={1} step={0.1}
          onInput={(v) => updateRoughness(v)}
          onCommit={(v) => changeProperty("roughness", v, 0.5)} />
      </Field>
      <Field label={japanese ? "金属度" : "Metalness"}>
        <Slider bind:value={metalness} min={0} max={1} step={0.1}
          onInput={(v) => updateMetalness(v)}
          onCommit={(v) => changeProperty("metalness", v, 0.0)} />
      </Field>
      <Field label={japanese ? "法線マップの強度" : "Normal Scale"}>
        <Slider bind:value={normalScale} min={0} max={10} step={0.1}
          onInput={(v) => updateNormalScale(v)}
          onCommit={(v) => changeProperty("normalScale", v, 1.0)} />
      </Field>
    </div>

  <!-- texture map -->
  {:else if activeTab === "adjust-texture-map"}
    <div class="tab-body">
      <div class="group-label">{japanese ? "平行移動" : "Translation"}</div>
      <div class="input-row">
        <Field label="X" row>
          <NumberInput bind:value={translationX} min={0} max={20} step={0.01} decimals={1}
            onInput={(v) => updateTextureMapOffset("x", v)}
            onCommit={(v) => changeProperty("offsetX", v, 0.0)} />
        </Field>
        <Field label="Y" row>
          <NumberInput bind:value={translationY} min={0} max={20} step={0.01} decimals={1}
            onInput={(v) => updateTextureMapOffset("y", v)}
            onCommit={(v) => changeProperty("offsetY", v, 0.0)} />
        </Field>
      </div>

      <div class="group-label">{japanese ? "回転" : "Rotation"}</div>
      <div class="input-row">
        <Field label="Z" row>
          <NumberInput bind:value={rotation} min={0} max={360} step={0.1} decimals={1} unit="°"
            onInput={(v) => updateTextureMapOrientation(v)}
            onCommit={(v) => changeProperty("rotation", v, 0)} />
        </Field>
      </div>

      <div class="group-label">{japanese ? "スケール" : "Scale"}</div>
      <div class="input-row">
        <Field label="XY" row>
          <NumberInput bind:value={scale} min={1} max={40} step={0.01} decimals={1}
            onInput={(v) => {
              scaleX = v;
              scaleY = v;
              updateTextureMapScale("x", v);
              updateTextureMapScale("y", v);
            }}
            onCommit={(v) => {
              changeProperty("scaleX", v, 1);
              changeProperty("scaleY", v, 1);
            }} />
        </Field>
        <Field label="X" row>
          <NumberInput bind:value={scaleX} min={1} max={40} step={0.01} decimals={1}
            onInput={(v) => updateTextureMapScale("x", v)}
            onCommit={(v) => changeProperty("scaleX", v, 1)} />
        </Field>
        <Field label="Y" row>
          <NumberInput bind:value={scaleY} min={1} max={40} step={0.01} decimals={1}
            onInput={(v) => updateTextureMapScale("y", v)}
            onCommit={(v) => changeProperty("scaleY", v, 1)} />
        </Field>
      </div>
    </div>

  <!-- color -->
  {:else if activeTab === "adjust-color"}
    <div class="tab-body">
      <div class="swatch-row">
        <!-- no-color swatch -->
        <button
          class="swatch"
          class:selected={selected_swatch_idx === undefined}
          style="background-color: {no_color.code};"
          title={japanese ? "色なし" : "No color"}
          onclick={() => (selected_swatch_idx = undefined)}
        >
          <Ban size={14} strokeWidth={1.75} color="#999" />
        </button>

        {#if selected_palette_idx != undefined && palettes.length > 0}
          {#each palettes[selected_palette_idx]["palette"] as swatch, i (i)}
            <button
              class="swatch"
              class:selected={selected_swatch_idx === i}
              style="background-color: {swatch};"
              aria-label={swatch}
              onclick={() => {
                selected_swatch_idx = i;
                commitColor();
              }}
            ></button>
          {/each}
        {/if}

        <button
          class="dropdown-toggle"
          title={japanese ? "パレットを選択" : "Select a palette"}
          onclick={() => (palette_dropdown_open = !palette_dropdown_open)}
        >
          <ChevronDown size={16} strokeWidth={1.75} />
        </button>
      </div>

      {#if palette_dropdown_open}
        <div class="palette-list">
          {#each palettes as p, j (j)}
            <button
              class="palette-option"
              class:selected={selected_palette_idx === j}
              onclick={() => {
                selected_palette_idx = j;
                selected_swatch_idx = 0;
                commitColor();
              }}
            >
              {#each p["palette"] as swatch, si (si)}
                <span class="mini-swatch" style="background-color: {swatch};"></span>
              {/each}
              <span class="palette-name">{p["name"]}</span>
            </button>
          {/each}
          <Button size="sm" variant="ghost" onclick={addNewColorPalette}>
            <Plus size={14} strokeWidth={1.75} />
            {japanese ? "新規追加" : "Add new"}
          </Button>
        </div>
      {/if}

      {#if selected_swatch_idx === undefined}
        <div class="no-color-note">{japanese ? "色なし" : "No color"}</div>
      {:else}
        <input
          class="color-picker"
          type="color"
          bind:value={palettes[selected_palette_idx]["palette"][selected_swatch_idx]}
          onchange={commitColor}
        />
      {/if}
    </div>

  {/if}
</div>

<style>
  .part-editor {
    display: flex;
    flex-direction: column;
    background: var(--bg-panel);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    margin-bottom: var(--sp-3);
    overflow: hidden;
    text-align: left;
  }

  .part-header {
    display: flex;
    gap: var(--sp-3);
    padding: var(--sp-3);
    border-bottom: 1px solid var(--border-subtle);
  }

  .preview {
    flex: none;
  }

  .part-meta {
    display: flex;
    flex-direction: column;
    gap: var(--sp-2);
    min-width: 0;
  }

  .part-title {
    font-size: var(--text-md);
    font-weight: 650;
    overflow-wrap: anywhere;
  }

  .part-title .parent {
    color: var(--text-secondary);
    font-weight: 500;
  }

  .part-title .sep {
    color: var(--text-muted);
    margin: 0 2px;
  }

  .meta-row {
    display: flex;
    align-items: center;
    gap: var(--sp-2);
    font-size: var(--text-sm);
    min-width: 0;
  }

  .meta-label {
    color: var(--text-muted);
    font-size: var(--text-xs);
    min-width: 48px;
  }

  .color-chip {
    width: 14px;
    height: 14px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border-strong);
    flex: none;
  }

  .color-code {
    color: var(--text-secondary);
    font-size: var(--text-xs);
  }

  .assistant-actions {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: var(--sp-2);
  }

  /* tabs */
  .editor-tabs {
    display: flex;
    border-bottom: 1px solid var(--border-subtle);
    padding: 0 var(--sp-2);
    gap: 2px;
    overflow-x: auto;
  }

  .editor-tab {
    border: none;
    background: transparent;
    color: var(--text-secondary);
    font-family: inherit;
    font-size: var(--text-sm);
    padding: var(--sp-2) var(--sp-2);
    border-bottom: 2px solid transparent;
    cursor: pointer;
    white-space: nowrap;
  }

  .editor-tab:hover {
    color: var(--text-primary);
  }

  .editor-tab.active {
    color: var(--text-primary);
    border-bottom-color: var(--accent);
  }

  .tab-body {
    display: flex;
    flex-direction: column;
    gap: var(--sp-3);
    padding: var(--sp-3);
  }

  .group-label {
    font-size: var(--text-xs);
    font-weight: 600;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }

  .input-row {
    display: flex;
    flex-wrap: wrap;
    gap: var(--sp-2) var(--sp-4);
  }

  /* color tab */
  .swatch-row {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: var(--sp-1);
  }

  .swatch {
    width: 26px;
    height: 26px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border-strong);
    cursor: pointer;
    display: grid;
    place-items: center;
    padding: 0;
  }

  .swatch.selected {
    outline: 2px solid var(--accent);
    outline-offset: 1px;
  }

  .dropdown-toggle {
    border: 1px solid var(--border-subtle);
    background: var(--bg-elevated);
    color: var(--text-secondary);
    border-radius: var(--radius-sm);
    width: 26px;
    height: 26px;
    display: grid;
    place-items: center;
    cursor: pointer;
  }

  .dropdown-toggle:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  .palette-list {
    display: flex;
    flex-direction: column;
    gap: var(--sp-1);
    background: var(--bg-elevated);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: var(--sp-2);
  }

  .palette-option {
    display: flex;
    align-items: center;
    gap: 3px;
    border: none;
    background: transparent;
    border-radius: var(--radius-sm);
    padding: var(--sp-1);
    cursor: pointer;
  }

  .palette-option:hover {
    background: var(--bg-hover);
  }

  .palette-option.selected {
    background: var(--accent-muted);
  }

  .mini-swatch {
    width: 14px;
    height: 14px;
    border-radius: 3px;
    border: 1px solid var(--border-strong);
  }

  .palette-name {
    margin-left: var(--sp-2);
    font-size: var(--text-xs);
    color: var(--text-secondary);
  }

  .no-color-note {
    color: var(--text-muted);
    font-size: var(--text-sm);
  }

  .color-picker {
    width: 64px;
    height: 36px;
    padding: 2px;
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    background: var(--bg-inset);
    cursor: pointer;
  }

  /* prompt ideas */
  .prompt-ideas {
    display: flex;
    flex-direction: column;
    gap: var(--sp-2);
    padding: var(--sp-2) var(--sp-3);
    border-bottom: 1px solid var(--border-subtle);
  }

  .ideas-label {
    display: flex;
    align-items: center;
    gap: var(--sp-1);
    font-size: var(--text-xs);
    font-weight: 600;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }

  .ideas-refreshing {
    font-weight: 400;
    text-transform: none;
    letter-spacing: normal;
    color: var(--text-muted);
  }

  .idea-chips {
    display: flex;
    flex-wrap: wrap;
    gap: var(--sp-1);
  }

  .idea-chip {
    border: 1px solid var(--border-subtle);
    background: var(--bg-elevated);
    color: var(--text-secondary);
    font-family: inherit;
    font-size: var(--text-xs);
    padding: 3px 10px;
    border-radius: var(--radius-full);
    cursor: pointer;
    text-align: left;
    transition:
      border-color 120ms ease,
      background 120ms ease,
      color 120ms ease;
  }

  .idea-chip:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
    border-color: var(--border-strong);
  }

  .idea-chip.material {
    border-left: 3px solid var(--accent);
  }

  .idea-chip.color {
    border-left: 3px solid #c084fc;
  }
</style>

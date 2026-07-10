<script>
    // Bulk editor (runes mode): applies finish / texture-map / color edits to
    // every currently selected part at once. Same onInput (live) vs onCommit
    // (history entry) contract as TexturePart.
    import { in_japanese, selected_objs_and_parts, curr_texture_parts, saved_color_palettes } from "../stores.js";
    import { addToHistory } from "../lib/history.js";
    import { get } from "svelte/store";
    import { onMount } from "svelte";

    import Slider from "../lib/ui/Slider.svelte";
    import NumberInput from "../lib/ui/NumberInput.svelte";
    import Button from "../lib/ui/Button.svelte";
    import Field from "../lib/ui/Field.svelte";

    import Plus from "@lucide/svelte/icons/plus";
    import Ban from "@lucide/svelte/icons/ban";
    import ChevronDown from "@lucide/svelte/icons/chevron-down";

    let japanese = $derived($in_japanese);

    let opacity = $state(1.0);
    let roughness = $state(0.5);
    let metalness = $state(0.0);
    let normalScale = $state(0.0);
    let displacementScale = $state(0.0);
    const material_color = "#FFFFFF";

    let translationX = $state(0.0);
    let translationY = $state(0.0);
    let rotation = $state(0.0);
    let scale = $state(1.0);
    let scaleX = $state(1.0);
    let scaleY = $state(1.0);

    let palettes = $state(get(saved_color_palettes));
    let selected_palette_idx = $state(0);
    let selected_swatch_idx = $state(undefined);
    const no_color = { name: "No Color", code: "#FFFFFF" };
    let palette_dropdown_open = $state(false);

    let activeTab = $state("adjust-finish");

    function addNewColorPalette() {
        palettes.push({
            name: "New Palette",
            palette: ["#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF"],
        });
        palettes = palettes;
        saved_color_palettes.set(palettes);
    }

    // ------------------------------------------------------- history commit

    function changeProperties(property, new_value, old_value = 0) {
        const sel = get(selected_objs_and_parts);
        const parts = get(curr_texture_parts);
        for (let i = 0; i < sel.length; i++) {
            const parent = sel[i]["parent"];
            const name = sel[i]["name"];
            if (parts[parent][name][property]) {
                old_value = parts[parent][name][property];
            }
            curr_texture_parts.update((value) => {
                value[parent][name][property] = new_value;
                return value;
            });
            addToHistory("Change " + property, parent, name, [property], [old_value], [new_value]);
        }
    }

    // ------------------------------------------------- live material updates

    function forEachSelected(fn) {
        selected_objs_and_parts.update((value) => {
            for (let i = 0; i < value.length; i++) {
                fn(value[i].model.children[0].material);
            }
            return value;
        });
    }

    function updateOpacities(v) {
        forEachSelected((material) => {
            material.transparent = true;
            material.opacity = v;
        });
    }

    function updateRoughnesses(v) {
        forEachSelected((material) => (material.roughness = v));
    }

    function updateMetalnesses(v) {
        forEachSelected((material) => (material.metalness = v));
    }

    function updateNormalScales(v) {
        forEachSelected((material) => {
            material.normalScale.x = v;
            material.normalScale.y = v;
        });
    }

    function updateDisplacementScales(v) {
        forEachSelected((material) => (material.displacementScale = v));
    }

    const ALL_MAPS = [
        "map", "normalMap", "aoMap", "alphaMap", "emissiveMap", "lightMap",
        "metalnessMap", "roughnessMap", "displacementMap", "bumpMap", "envMap",
    ];

    function forEachMapOfSelected(fn) {
        forEachSelected((material) => {
            for (const key of ALL_MAPS) {
                if (material[key]) fn(material[key]);
            }
        });
    }

    function degreeToRadians(degrees) {
        return degrees * (Math.PI / 180);
    }

    function updateTextureMapOffsets(x_or_y, v) {
        forEachMapOfSelected((map) => (map.offset[x_or_y] = v));
    }

    function updateTextureMapScales(x_or_y, v) {
        forEachMapOfSelected((map) => (map.repeat[x_or_y] = v));
    }

    function updateTextureMapOrientations(rot) {
        forEachMapOfSelected((map) => (map.rotation = degreeToRadians(rot)));
    }

    // ----------------------------------------------------------- color logic

    function updateColors() {
        const color = palettes[selected_palette_idx]["palette"][selected_swatch_idx];
        const hexNumber = parseInt(color.substring(1), 16);
        forEachSelected((material) => {
            material.color.setHex(hexNumber);
            material.color_hex = hexNumber;
        });
    }

    function commitColors() {
        updateColors();
        changeProperties("color", palettes[selected_palette_idx]["palette"][selected_swatch_idx], "#FFFFFF");
    }

    onMount(() => {
        if (material_color) {
            palettes.unshift({
                name: "Custom",
                palette: [material_color, "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF"],
            });
            palettes = palettes;
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

<div class="bulk-editor">
    <div class="bulk-header">
        {japanese ? "複数のオブジェクトを制御する" : "Edit All Selected"}
        <span class="count">{$selected_objs_and_parts.length}</span>
    </div>

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

    {#if activeTab === "adjust-finish"}
        <div class="tab-body">
            <Field label={japanese ? "透明度" : "Opacity"}>
                <Slider bind:value={opacity} min={0} max={1} step={0.1}
                    onInput={(v) => updateOpacities(v)}
                    onCommit={(v) => changeProperties("opacity", v, 1.0)} />
            </Field>
            <Field label={japanese ? "光沢" : "Roughness"}>
                <Slider bind:value={roughness} min={0} max={1} step={0.1}
                    onInput={(v) => updateRoughnesses(v)}
                    onCommit={(v) => changeProperties("roughness", v, 0.5)} />
            </Field>
            <Field label={japanese ? "金属度" : "Metalness"}>
                <Slider bind:value={metalness} min={0} max={1} step={0.1}
                    onInput={(v) => updateMetalnesses(v)}
                    onCommit={(v) => changeProperties("metalness", v, 0.5)} />
            </Field>
            <Field label={japanese ? "法線マップの強度" : "Normal Scale"}>
                <Slider bind:value={normalScale} min={0} max={10} step={0.1}
                    onInput={(v) => updateNormalScales(v)}
                    onCommit={(v) => changeProperties("normalScale", v, 0.5)} />
            </Field>
            <Field label={japanese ? "高さマップの強度" : "Height Scale"}>
                <Slider bind:value={displacementScale} min={0} max={0.5} step={0.01}
                    onInput={(v) => updateDisplacementScales(v)}
                    onCommit={(v) => changeProperties("displacementScale", v, 0.0)} />
            </Field>
        </div>
    {:else if activeTab === "adjust-texture-map"}
        <div class="tab-body">
            <div class="group-label">{japanese ? "平行移動" : "Translation"}</div>
            <div class="input-row">
                <Field label="X" row>
                    <NumberInput bind:value={translationX} min={0} max={20} step={0.01} decimals={1}
                        onInput={(v) => updateTextureMapOffsets("x", v)}
                        onCommit={(v) => changeProperties("offsetX", v, 0.0)} />
                </Field>
                <Field label="Y" row>
                    <NumberInput bind:value={translationY} min={0} max={20} step={0.01} decimals={1}
                        onInput={(v) => updateTextureMapOffsets("y", v)}
                        onCommit={(v) => changeProperties("offsetY", v, 0.0)} />
                </Field>
            </div>

            <div class="group-label">{japanese ? "回転" : "Rotation"}</div>
            <div class="input-row">
                <Field label="Z" row>
                    <NumberInput bind:value={rotation} min={0} max={360} step={0.1} decimals={1} unit="°"
                        onInput={(v) => updateTextureMapOrientations(v)}
                        onCommit={(v) => changeProperties("rotation", v, 0)} />
                </Field>
            </div>

            <div class="group-label">{japanese ? "スケール" : "Scale"}</div>
            <div class="input-row">
                <Field label="XY" row>
                    <NumberInput bind:value={scale} min={1} max={40} step={0.01} decimals={1}
                        onInput={(v) => {
                            scaleX = v;
                            scaleY = v;
                            updateTextureMapScales("x", v);
                            updateTextureMapScales("y", v);
                        }}
                        onCommit={(v) => {
                            changeProperties("scaleX", v, 1);
                            changeProperties("scaleY", v, 1);
                        }} />
                </Field>
                <Field label="X" row>
                    <NumberInput bind:value={scaleX} min={1} max={40} step={0.01} decimals={1}
                        onInput={(v) => updateTextureMapScales("x", v)}
                        onCommit={(v) => changeProperties("scaleX", v, 1)} />
                </Field>
                <Field label="Y" row>
                    <NumberInput bind:value={scaleY} min={1} max={40} step={0.01} decimals={1}
                        onInput={(v) => updateTextureMapScales("y", v)}
                        onCommit={(v) => changeProperties("scaleY", v, 1)} />
                </Field>
            </div>
        </div>
    {:else if activeTab === "adjust-color"}
        <div class="tab-body">
            <div class="swatch-row">
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
                                commitColors();
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
                                commitColors();
                            }}
                        >
                            {#each p["palette"] as swatch}
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
                    onchange={commitColors}
                />
            {/if}
        </div>
    {/if}
</div>

<style>
    .bulk-editor {
        display: flex;
        flex-direction: column;
        background: var(--bg-elevated);
        border: 1px solid var(--accent-muted);
        border-radius: var(--radius-lg);
        margin-bottom: var(--sp-3);
        overflow: hidden;
        text-align: left;
    }

    .bulk-header {
        display: flex;
        align-items: center;
        gap: var(--sp-2);
        padding: var(--sp-3);
        font-size: var(--text-sm);
        font-weight: 650;
        border-bottom: 1px solid var(--border-subtle);
    }

    .count {
        font-size: var(--text-xs);
        font-weight: 500;
        color: var(--accent);
        background: var(--accent-muted);
        border-radius: var(--radius-full);
        padding: 0 6px;
        line-height: 16px;
    }

    .editor-tabs {
        display: flex;
        border-bottom: 1px solid var(--border-subtle);
        padding: 0 var(--sp-2);
        gap: 2px;
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
        background: var(--bg-panel);
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
        background: var(--bg-panel);
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
</style>

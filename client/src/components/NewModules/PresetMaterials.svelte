<script>
    import { onMount } from 'svelte';
    import { get } from 'svelte/store';

    import { design_brief, in_japanese } from '../../stores.js';
    import { pollJob } from '../../lib/jobs.js';
    import { showToast } from '../../lib/toast.js';

    import DynamicImage from '../DynamicImage.svelte';
    import PanelSection from '../../lib/ui/PanelSection.svelte';
    import TextArea from '../../lib/ui/TextArea.svelte';
    import Button from '../../lib/ui/Button.svelte';
    import NumberInput from '../../lib/ui/NumberInput.svelte';
    import Switch from '../../lib/ui/Switch.svelte';
    import Field from '../../lib/ui/Field.svelte';
    import Spinner from '../../lib/ui/Spinner.svelte';

    let japanese = $derived($in_japanese);

    let preset_materials = $state({});
    let loading_presets = $state(true);

    let selected_texture = ""; // not rendered directly; scratch value for the fetch bodies below
    let selected_material_name = $state("");
    let use_design_brief = $state(true);

    let suggestions = $state([]);
    let prompt = $state("");

    let toOutputGrid = $state(false);
    let n = $state(4);
    let is_exploring = $state(false);

    let context = get(design_brief);

    async function loadPresetMaterials() {
        let response = await fetch('/get_preset_materials');
        let data = await response.json();

        // preset_materials is now: {name: {diffuse, normal, height}}
        return data["preset_materials"];
    }

    onMount(async function () {
        try {
            preset_materials = await loadPresetMaterials();
            console.log("Preset materials: ", preset_materials);
            context = get(design_brief);
        } finally {
            loading_presets = false;
        }
    });

    function deselect(name) {
        if (selected_material_name === name) {
            selected_material_name = "";
        }
    }

    async function explore_materials() {
        toOutputGrid = false;
        suggestions = [];
        if (selected_material_name === "") {
            showToast(japanese ? "先に素材を選択してください" : "Please select a material first", 'error');
            return;
        }
        selected_texture = preset_materials[selected_material_name]["diffuse"];

        is_exploring = true;
        try {
            let material_response = await fetch("/get_materials", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    "prompt": prompt,
                    "n": n,
                    "design_brief": use_design_brief ? context : null,
                    "image_path": selected_texture,
                    "material_name": selected_material_name
                }),
            });

            let materials_json = await material_response.json();
            let texture_prompts = materials_json["prompts"];
            let materials = materials_json["materials"];
            let explanations = materials_json["explanations"];

            console.log("Texture prompts: ", texture_prompts);

            // Generate n textures from the prompts
            for (let i=0; i<texture_prompts.length; i++) {
                let texture_string = texture_prompts[i] + " texture map, seamless, 4k";

                let texture_response = await fetch("/generate_textures", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({
                        "texture_string": texture_string,
                        "n":1,
                        "imsize":448,
                    }),
                });
                let results_json = await texture_response.json();
                let result_payload = results_json;
                if (results_json && results_json["job_id"]) {
                    result_payload = await pollJob(results_json["job_id"]);
                }
                let result = result_payload["results"][0];
                let texture_map = result["texture"]
                suggestions.push({
                    "material": materials[i],
                    "texture_map": texture_map,
                    "explanation": explanations[i]
                });
            }

            console.log("Suggestions: ", suggestions);
        } finally {
            is_exploring = false;
        }
    }

    async function explore_textures() {
        suggestions = [];
        if (selected_material_name === "") {
            showToast(japanese ? "先に素材を選択してください" : "Please select a material first", 'error');
            return;
        }
        selected_texture = preset_materials[selected_material_name]["diffuse"];
        // Get n material prompts from chatgpt
        toOutputGrid = true;

        is_exploring = true;
        try {
            let prompt_response = await fetch("/get_texture_prompts", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    "prompt": prompt,
                    "n": n,
                    "design_brief": use_design_brief ? context : null,
                    "image_path": selected_texture,
                }),
            });

            let prompts_json = await prompt_response.json();
            let texture_prompts = prompts_json["texture_prompts"];
            console.log("Texture prompts: ", texture_prompts);

            // Generate n textures from the prompts
            for (let i=0; i<texture_prompts.length; i++) {
                let texture_string = texture_prompts[i] + " texture map, seamless, 4k";

                let texture_response = await fetch("/generate_textures", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({
                        "texture_string": texture_string,
                        "n":1,
                        "imsize":448,
                    }),
                });
                let results_json = await texture_response.json();
                let result_payload = results_json;
                if (results_json && results_json["job_id"]) {
                    result_payload = await pollJob(results_json["job_id"]);
                }
                let result = result_payload["results"][0];
                let texture_map = result["texture"]
                suggestions.push({"texture_map": texture_map});
            }

            console.log("Suggestions: ", suggestions);
        } finally {
            is_exploring = false;
        }
    }

</script>

<div class="preset-materials">
    <PanelSection title={japanese ? "素材ライブラリ" : "Material Library"}>
        {#if loading_presets}
            <div class="state-message">
                <Spinner size={24} />
            </div>
        {:else if Object.keys(preset_materials).length === 0}
            <div class="state-message muted">
                {japanese ? "プリセット素材が見つかりません。" : "No preset materials found."}
            </div>
        {:else}
            <div class="preset-grid">
                {#each Object.entries(preset_materials) as [name, maps] (name)}
                    <label class="preset-item" class:selected={selected_material_name === name}>
                        <input
                            type="radio"
                            class="sr-only"
                            name="preset-material"
                            value={name}
                            bind:group={selected_material_name}
                            onclick={() => deselect(name)}
                        />
                        <div class="thumb-wrap">
                            <DynamicImage imagepath={maps.diffuse} alt={name} size="100%" is_draggable={true} />
                        </div>
                        <span class="preset-name">{name}</span>
                    </label>
                {/each}
            </div>
        {/if}
    </PanelSection>

    <PanelSection title={japanese ? "候補を探す" : "Explore"}>
        <div class="explore-form">
            <TextArea bind:value={prompt} placeholder="(Optional) Enter your prompt here.." />

            <div class="explore-actions">
                <Button variant="primary" onclick={explore_textures} loading={is_exploring} disabled={is_exploring}>
                    {japanese ? "テクスチャーを探す" : "Explore Textures"}
                </Button>
                <Button variant="primary" onclick={explore_materials} loading={is_exploring} disabled={is_exploring}>
                    {japanese ? "素材を探す" : "Explore Materials"}
                </Button>
            </div>

            <div class="explore-options">
                <Field label={japanese ? "出力数" : "Number of Outputs"} row>
                    <NumberInput bind:value={n} min={1} max={10} step={1} />
                </Field>
                <Switch bind:checked={use_design_brief} label={japanese ? "デザインブリーフ" : "Design brief"} />
            </div>
        </div>
    </PanelSection>

    <PanelSection title={japanese ? "候補" : "Suggestions"}>
        {#if is_exploring}
            <div class="state-message">
                <Spinner size={24} />
            </div>
        {:else if suggestions.length === 0}
            <div class="state-message muted">
                {japanese
                    ? "上のボタンでテクスチャーまたは素材を探してください。"
                    : "Explore textures or materials above to see suggestions here."}
            </div>
        {:else if toOutputGrid}
            <div class="suggestion-grid">
                {#each suggestions as suggestion}
                    <div class="thumb-wrap">
                        <DynamicImage imagepath={suggestion.texture_map} alt="suggestion" size="100%" is_draggable={true} />
                    </div>
                {/each}
            </div>
        {:else}
            <div class="suggestion-list">
                {#each suggestions as suggestion}
                    <div class="suggestion-row">
                        <div class="thumb-wrap suggestion-thumb">
                            <DynamicImage imagepath={suggestion.texture_map} alt={suggestion.material} size="100%" is_draggable={true} />
                        </div>
                        <div class="suggestion-info">
                            <div class="suggestion-material">{suggestion.material}</div>
                            <p class="suggestion-explanation">{suggestion.explanation}</p>
                        </div>
                    </div>
                {/each}
            </div>
        {/if}
    </PanelSection>
</div>

<style>
    .preset-materials {
        display: flex;
        flex-direction: column;
        gap: var(--sp-4);
        width: 100%;
    }

    .state-message {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: var(--sp-5) 0;
    }

    .state-message.muted {
        color: var(--text-muted);
        font-size: var(--text-sm);
        text-align: center;
    }

    /* --- Preset library grid --- */

    .preset-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(96px, 1fr));
        gap: var(--sp-3);
    }

    .preset-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: var(--sp-1);
        cursor: pointer;
    }

    .sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border: 0;
    }

    .thumb-wrap {
        position: relative;
        aspect-ratio: 1 / 1;
        border-radius: var(--radius-md);
    }

    .preset-grid .thumb-wrap,
    .suggestion-grid .thumb-wrap {
        width: 100%;
    }

    .preset-item input:focus-visible + .thumb-wrap {
        box-shadow: var(--ring);
    }

    .preset-item.selected .thumb-wrap {
        box-shadow: 0 0 0 2px var(--accent);
    }

    .preset-name {
        width: 100%;
        font-size: var(--text-xs);
        color: var(--text-secondary);
        text-align: center;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .preset-item.selected .preset-name {
        color: var(--text-primary);
    }

    /* --- Explore form --- */

    .explore-form {
        display: flex;
        flex-direction: column;
        gap: var(--sp-3);
    }

    .explore-actions {
        display: flex;
        gap: var(--sp-2);
    }

    .explore-actions :global(button) {
        flex: 1;
    }

    .explore-options {
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: var(--sp-3);
    }

    /* --- Suggestions --- */

    .suggestion-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(96px, 1fr));
        gap: var(--sp-3);
    }

    .suggestion-list {
        display: flex;
        flex-direction: column;
        gap: var(--sp-3);
    }

    .suggestion-row {
        display: flex;
        align-items: flex-start;
        gap: var(--sp-3);
    }

    .suggestion-thumb {
        width: 96px;
        flex-shrink: 0;
    }

    .suggestion-info {
        display: flex;
        flex-direction: column;
        gap: var(--sp-1);
        min-width: 0;
    }

    .suggestion-material {
        font-size: var(--text-sm);
        font-weight: 600;
        color: var(--text-primary);
    }

    .suggestion-explanation {
        margin: 0;
        font-size: var(--text-xs);
        color: var(--text-secondary);
        line-height: 1.4;
    }
</style>

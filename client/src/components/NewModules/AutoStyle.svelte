<!--
  AutoStyle.svelte — "Auto-style" tab: one LLM call assigns a coherent
  material + color to every selectable part of the scene.

  PROPS: none required. Like PresetMaterials.svelte, this component reads
  everything it needs from the shared stores (stores.js):
    - curr_texture_parts        : {object: {part: {...part manifest...}}}
                                   used both to collect the selectable
                                   part list to send to /api/auto_style and
                                   to write color/roughness/metalness before
                                   applying a texture.
    - lib/registry.js viewport  : imperative surface of ThreeDDisplay.svelte
                                   (registered on its mount); calls its
                                   exported transferTexture(object, part,
                                   mat_name, diffuse_path, normal_path,
                                   height_path) once per accepted row.
    - in_japanese                : bilingual label toggle.

  Already wired in: ActionsPanel.svelte imports this component and mounts it
  in the `auto_style` tab-content div; App.svelte's icon rail (WandSparkles,
  id 'auto_style') drives `actions_panel_tab` to switch to it. No further
  wiring is needed for this component to appear.

  APPLY / HISTORY MECHANISM (see report for rationale):
  For each accepted row we (1) write color/roughness/metalness onto
  curr_texture_parts[object][part] via curr_texture_parts.update (the same
  store TexturePart.svelte's changeProperty() mutates), capturing the old
  values first, then (2) call
  viewport.get().transferTexture(object, part, material_name, diffuse,
  normal, height) — the same exported function DynamicImage's
  apply_texture()/fullTextureTransferAlgorithm() drive, addressed directly
  by object/part name instead of via the current 3D-view selection — and
  finally (3) call addToHistory("Change Texture", ...) exactly like
  ThreeDDisplay.svelte's fullTextureTransferAlgorithm does, but with the
  additional color/roughness/metalness old/new pairs folded into the SAME
  history entry (addToHistory accepts arbitrary property lists; the
  "Change Texture" name is what triggers lib/history.js's special copy-old-and-new
  texture-files-into-history-slot handling, which only reads the
  mat_image_texture/mat_normal_texture/mat_height_texture keys and ignores
  the rest). This gives ONE history/undo entry per applied part, matching
  the task's instruction, while still reusing the existing undo plumbing
  as-is (no changes to lib/history.js/ThreeDDisplay.svelte).
-->
<script>
    import { get } from 'svelte/store';

    import { curr_texture_parts, in_japanese } from '../../stores.js';
    import { viewport } from '../../lib/registry.js';
    import { showToast } from '../../lib/toast.js';
    import { pollJob } from '../../lib/jobs.js';
    import { addToHistory } from '../../lib/history.js';

    import DynamicImage from '../DynamicImage.svelte';
    import Button from '../../lib/ui/Button.svelte';
    import TextInput from '../../lib/ui/TextInput.svelte';
    import Spinner from '../../lib/ui/Spinner.svelte';

    let japanese = $derived($in_japanese);

    const STYLE_CHIPS = [
        { key: 'Scandinavian', en: 'Scandinavian', ja: '北欧' },
        { key: 'Industrial', en: 'Industrial', ja: 'インダストリアル' },
        { key: 'Japandi', en: 'Japandi', ja: 'ジャパンディ' },
        { key: 'Mid-century', en: 'Mid-century', ja: 'ミッドセンチュリー' },
        { key: 'Coastal', en: 'Coastal', ja: 'コースタル' },
    ];

    let selected_chip = $state('');
    let custom_style = $state('');

    let is_loading = $state(false);
    let progress = $state(0.0);
    let progress_message = $state('');

    let style_used = $state('');
    let rows = $state([]); // [{object, part, material_name, diffuse, normal, height, color, roughness, metalness, source, included}]
    let has_result = $state(false);
    let is_applying = $state(false);

    let included_count = $derived(rows.filter(r => r.included).length);

    function selectChip(key) {
        selected_chip = key;
        custom_style = '';
    }

    function currentStyle() {
        return (custom_style && custom_style.trim()) ? custom_style.trim() : selected_chip;
    }

    function collectSelectableParts() {
        const parts_dict = get(curr_texture_parts);
        const parts = [];
        for (const obj in parts_dict) {
            for (const part in parts_dict[obj]) {
                if (parts_dict[obj][part] && parts_dict[obj][part]['is_selectable']) {
                    parts.push({ object: obj, part: part });
                }
            }
        }
        return parts;
    }

    async function styleMyScene() {
        const style = currentStyle();
        if (!style) {
            showToast(japanese ? "スタイルを選択するか、入力してください。" : "Please choose or enter a style first.", 'error');
            return;
        }

        const parts = collectSelectableParts();
        if (parts.length === 0) {
            showToast(japanese ? "選択可能なパーツが見つかりません。" : "No selectable parts found in the scene.", 'error');
            return;
        }

        is_loading = true;
        progress = 0;
        progress_message = japanese ? "開始しています..." : "Starting...";
        has_result = false;
        rows = [];

        try {
            const response = await fetch("/api/auto_style", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ style: style, parts: parts }),
            });
            if (!response.ok) {
                const err_json = await response.json().catch(() => ({}));
                throw new Error(err_json.error || `Request failed (${response.status})`);
            }
            const data = await response.json();

            const result = await pollJob(data.job_id, {
                onProgress: (job) => {
                    progress = job.progress || 0;
                    progress_message = job.message || '';
                }
            });

            style_used = result.style;
            rows = result.assignments.map(a => ({ ...a, included: true }));
            has_result = true;
        } catch (error) {
            console.error(error);
            showToast(
                japanese ? `オートスタイルに失敗しました：${error.message}` : `Auto-style failed: ${error.message}`,
                'error'
            );
        } finally {
            is_loading = false;
        }
    }

    async function applyRow(row) {
        const current = get(curr_texture_parts);
        const part_entry = current[row.object] && current[row.object][row.part];
        if (!part_entry) {
            console.error(`AutoStyle: part not found in curr_texture_parts: ${row.object}/${row.part}`);
            return;
        }

        // Capture old values before mutating, for the single history entry.
        const old_mat_name = part_entry['mat_name'] ?? null;
        const old_mat_image_texture = part_entry['mat_image_texture'] ?? null;
        const old_mat_normal_texture = part_entry['mat_normal_texture'] ?? null;
        const old_mat_height_texture = part_entry['mat_height_texture'] ?? null;
        const old_color = part_entry['color'] ?? "#FFFFFF";
        const old_roughness = part_entry['roughness'] ?? 0.5;
        const old_metalness = part_entry['metalness'] ?? 0.0;

        // Write the new finish values into the store BEFORE calling
        // transferTexture(): ThreeDDisplay.svelte's transferTexture() reads
        // color/roughness/metalness for the part straight out of this same
        // store when it builds the material, so this is how a "batch" apply
        // gets its per-part color/finish across to the 3D view.
        curr_texture_parts.update(value => {
            value[row.object][row.part]['color'] = row.color;
            value[row.object][row.part]['roughness'] = row.roughness;
            value[row.object][row.part]['metalness'] = row.metalness;
            return value;
        });

        await viewport.get()?.transferTexture(
            row.object, row.part, row.material_name, row.diffuse, row.normal, row.height
        );

        const updated = get(curr_texture_parts);
        const new_mat_image_texture = updated[row.object][row.part]['mat_image_texture'];
        const new_mat_normal_texture = updated[row.object][row.part]['mat_normal_texture'];
        const new_mat_height_texture = updated[row.object][row.part]['mat_height_texture'];

        // ONE history entry per applied part: "Change Texture" is required
        // (not just any name) so lib/history.js's addToHistory copies the old/new
        // texture files into per-history-index storage for undo/redo; the
        // extra color/roughness/metalness pairs ride along in the same entry.
        await addToHistory(
            "Change Texture",
            row.object, row.part,
            ["mat_name", "mat_image_texture", "mat_normal_texture", "mat_height_texture",
             "color", "roughness", "metalness"],
            [old_mat_name, old_mat_image_texture, old_mat_normal_texture, old_mat_height_texture,
             old_color, old_roughness, old_metalness],
            [row.material_name, new_mat_image_texture, new_mat_normal_texture, new_mat_height_texture,
             row.color, row.roughness, row.metalness]
        );
    }

    async function applyAll() {
        if (!viewport.get()) {
            showToast(japanese ? "3Dビューの準備ができていません。" : "3D view is not ready yet.", 'error');
            return;
        }
        const to_apply = rows.filter(r => r.included);
        if (to_apply.length === 0) {
            showToast(japanese ? "適用するパーツがありません。" : "No parts selected to apply.", 'error');
            return;
        }

        is_applying = true;
        let applied = 0;
        try {
            for (const row of to_apply) {
                try {
                    await applyRow(row);
                    applied++;
                } catch (error) {
                    console.error(`AutoStyle: failed to apply ${row.object}/${row.part}`, error);
                }
            }
            showToast(
                japanese ? `${applied}個のパーツにスタイルを適用しました。` : `Applied style to ${applied} part(s).`,
                'success'
            );
        } finally {
            is_applying = false;
        }
    }

</script>

<div class="auto-style-module">
    <div class="header">
        <h2 class="title">{japanese ? "オートスタイル" : "Auto-Style"}</h2>
        <p class="description">
            {japanese
                ? "スタイルを選択すると、シーン内のすべての選択可能なパーツに一貫した素材と色を一括で割り当てます。"
                : "Pick a style and assign a coherent material + color to every selectable part of the scene in one shot."}
        </p>
    </div>

    <div class="chip-row">
        {#each STYLE_CHIPS as chip (chip.key)}
            <button
                type="button"
                class="chip"
                class:selected={selected_chip === chip.key && !custom_style}
                onclick={() => selectChip(chip.key)}
            >
                {japanese ? chip.ja : chip.en}
            </button>
        {/each}
    </div>

    <TextInput
        placeholder={japanese ? "（任意）自由入力のスタイル..." : "(Optional) Enter a custom style..."}
        bind:value={custom_style}
    />

    <Button variant="primary" fullWidth loading={is_loading} onclick={styleMyScene}>
        {japanese ? "シーンをスタイリング" : "Style my scene"}
    </Button>

    {#if is_loading}
        <div class="progress-row">
            <Spinner size={16} />
            <span class="progress-text">
                {progress_message}{progress > 0 ? ` (${Math.round(progress * 100)}%)` : ''}
            </span>
        </div>
    {/if}

    {#if has_result}
        <div class="results">
            <h3 class="results-heading">
                {japanese ? `結果（スタイル：${style_used}）` : `Results (style: ${style_used})`}
                — {included_count} / {rows.length} {japanese ? "選択中" : "included"}
            </h3>

            <div class="rows-table">
                {#each rows as row (row.object + "|" + row.part)}
                    <div class="row-item">
                        <input type="checkbox" class="row-check" bind:checked={row.included} />

                        <DynamicImage imagepath={row.diffuse} alt={row.material_name} size="36px" />

                        <div class="row-main">
                            <span class="part-name">{row.object} / {row.part}</span>
                            <span class="material-name">{row.material_name}</span>
                        </div>

                        <span class="swatch" style:background-color={row.color}></span>

                        <div class="row-numbers">
                            <span>{japanese ? "光沢" : "rough"}: {row.roughness.toFixed(2)}</span>
                            <span>{japanese ? "金属度" : "metal"}: {row.metalness.toFixed(2)}</span>
                        </div>

                        <span class="badge" class:generate={row.source === 'generate'}>
                            {row.source === 'generate'
                                ? (japanese ? "生成" : "generated")
                                : (japanese ? "プリセット" : "preset")}
                        </span>
                    </div>
                {/each}
            </div>

            <Button variant="primary" fullWidth loading={is_applying} onclick={applyAll}>
                {is_applying
                    ? (japanese ? "適用中..." : "Applying...")
                    : (japanese ? "適用" : "Apply")}
            </Button>
        </div>
    {/if}
</div>

<style>
    .auto-style-module {
        display: flex;
        flex-direction: column;
        gap: var(--sp-3);
        width: 100%;
        overflow: auto;
    }

    .header {
        display: flex;
        flex-direction: column;
        gap: var(--sp-1);
    }

    .title {
        margin: 0;
        font-size: var(--text-sm);
        font-weight: 600;
        color: var(--text-primary);
    }

    .description {
        margin: 0;
        font-size: var(--text-base);
        color: var(--text-secondary);
    }

    .chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: var(--sp-2);
    }

    .chip {
        height: 24px;
        padding: 0 var(--sp-3);
        border-radius: var(--radius-full);
        background: var(--bg-elevated);
        border: 1px solid var(--border-subtle);
        color: var(--text-secondary);
        font-family: var(--font-sans);
        font-size: var(--text-sm);
        cursor: pointer;
        transition:
            background 120ms ease,
            border-color 120ms ease,
            color 120ms ease;
    }

    .chip:hover {
        border-color: var(--border-strong);
        color: var(--text-primary);
    }

    .chip.selected {
        background: var(--accent-muted);
        border-color: var(--accent);
        color: var(--accent);
    }

    .progress-row {
        display: flex;
        align-items: center;
        gap: var(--sp-2);
    }

    .progress-text {
        font-size: var(--text-xs);
        color: var(--text-secondary);
    }

    .results {
        display: flex;
        flex-direction: column;
        gap: var(--sp-2);
        min-height: 0;
    }

    .results-heading {
        margin: 0;
        font-size: var(--text-sm);
        font-weight: 600;
        color: var(--text-primary);
    }

    .rows-table {
        display: flex;
        flex-direction: column;
        max-height: 50vh;
        overflow: auto;
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        padding: 0 var(--sp-3);
    }

    .row-item {
        display: flex;
        align-items: center;
        gap: var(--sp-3);
        padding: var(--sp-2) 0;
        border-bottom: 1px solid var(--border-subtle);
    }

    .row-item:last-child {
        border-bottom: none;
    }

    .row-check {
        flex-shrink: 0;
        width: 14px;
        height: 14px;
        accent-color: var(--accent);
        cursor: pointer;
    }

    .row-main {
        display: flex;
        flex-direction: column;
        flex: 1;
        min-width: 0;
        gap: 2px;
    }

    .part-name {
        font-size: var(--text-base);
        font-weight: 500;
        color: var(--text-primary);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .material-name {
        font-size: var(--text-sm);
        color: var(--text-secondary);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .swatch {
        flex-shrink: 0;
        width: 16px;
        height: 16px;
        border-radius: var(--radius-sm);
        border: 1px solid var(--border-subtle);
    }

    .row-numbers {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        flex-shrink: 0;
        gap: 2px;
        font-size: var(--text-xs);
        color: var(--text-muted);
    }

    .badge {
        flex-shrink: 0;
        font-size: var(--text-xs);
        padding: 1px var(--sp-2);
        border-radius: var(--radius-full);
        background: var(--bg-elevated);
        border: 1px solid var(--border-subtle);
        color: var(--text-secondary);
        white-space: nowrap;
    }

    .badge.generate {
        background: var(--accent-muted);
        border-color: var(--accent);
        color: var(--accent);
    }
</style>

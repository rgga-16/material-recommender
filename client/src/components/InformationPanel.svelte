<script>
    // Inspector panel (runes mode): shows one TexturePart editor per selected
    // part, plus the bulk TextureParts editor when several parts are selected.
    import { onDestroy } from 'svelte';
    import TexturePart from './TexturePart.svelte';
    import TextureParts from './TextureParts.svelte';

    import { selected_objs_and_parts, in_japanese } from '../stores.js';
    import { inspector } from '../lib/registry.js';

    let japanese = $derived($in_japanese);

    // Deselection is store-driven (selected_objs_and_parts becomes []), which
    // re-renders this template; the exported function remains for the registry
    // contract with the 3D viewport.
    export function clearTexturePart() {}

    onDestroy(inspector.register({ clearTexturePart }));
</script>

<div class="inspector-panel">
    <div class="inspector-header">
        {japanese ? "オブジェクト詳細" : "Object Details"}
        {#if $selected_objs_and_parts.length > 0}
            <span class="count">{$selected_objs_and_parts.length}</span>
        {/if}
    </div>

    <div class="inspector-body" id="texture-part-details">
        {#if $selected_objs_and_parts.length > 0}
            {#if $selected_objs_and_parts.length > 1}
                <TextureParts />
            {/if}
            {#each $selected_objs_and_parts as sel_obj_part, i (sel_obj_part.parent + '/' + sel_obj_part.name)}
                <TexturePart
                    index={i}
                    part_parent_name={sel_obj_part.parent}
                    part_name={sel_obj_part.name}
                />
            {/each}
        {:else}
            <div class="empty-state">
                {japanese
                    ? "オブジェクトが選択されていません。3Dビューでオブジェクトを選択してください。"
                    : "No object selected. Select an object in the 3D view to edit its material."}
            </div>
        {/if}
    </div>
</div>

<style>
    .inspector-panel {
        display: flex;
        flex-direction: column;
        height: 100%;
    }

    .inspector-header {
        flex: none;
        display: flex;
        align-items: center;
        gap: var(--sp-2);
        padding: var(--sp-3) var(--sp-4);
        font-size: var(--text-sm);
        font-weight: 650;
        border-bottom: 1px solid var(--border-subtle);
    }

    .count {
        font-size: var(--text-xs);
        font-weight: 500;
        color: var(--text-muted);
        background: var(--bg-inset);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-full);
        padding: 0 6px;
        line-height: 16px;
    }

    .inspector-body {
        flex: 1;
        min-height: 0;
        overflow-y: auto;
        padding: var(--sp-3);
    }

    .empty-state {
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        height: 60%;
        color: var(--text-muted);
        font-size: var(--text-sm);
        padding: var(--sp-4);
        line-height: 1.6;
    }
</style>

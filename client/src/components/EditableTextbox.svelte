<script>
    import { curr_texture_parts, in_japanese } from '../stores.js';
    import { get } from 'svelte/store';
    import { onMount } from 'svelte';

    import Button from '../lib/ui/Button.svelte';
    import TextInput from '../lib/ui/TextInput.svelte';

    let { text = $bindable() } = $props();

    let japanese = $derived($in_japanese);

    let temp_val = $state("");

    let is_editing = $state(false);

    function edit() {
        is_editing = true;
    }

    function save() {
        text = temp_val;
        is_editing = false;
        console.log(get(curr_texture_parts));
    }

    function cancel() {
        is_editing = false;
    }

    onMount(() => {
        temp_val = text;
    });
</script>

<div class="container">
    <TextInput bind:value={temp_val} readonly={!is_editing} />
    {#if is_editing}
        <Button variant="secondary" size="sm" onclick={cancel}>{japanese ? "キャンセル" : "Cancel"}</Button>
        <Button variant="primary" size="sm" onclick={save}>{japanese ? "保存する" : "Save"}</Button>
    {:else}
        <Button variant="secondary" size="sm" onclick={edit}>{japanese ? "編集" : "Edit"}</Button>
    {/if}
</div>


<style>
    .container {
        display: flex;
        flex-direction: row;
        align-items: center;
        gap: var(--sp-1);
        padding: var(--sp-1);
    }

    .container :global(.text-input) {
        flex: 1 1 auto;
        min-width: 0;
    }
</style>

<script>
    export let text;
    import {curr_texture_parts, in_japanese} from '../stores.js';
    import {get} from 'svelte/store';
    import {onMount} from 'svelte';

    let japanese;
    in_japanese.subscribe(value => {
        japanese = value;
    });

    let temp_val="";

    let is_editing=false;
    
    function edit() {
        is_editing=true;
    }

    function save() {
        text = temp_val;
        is_editing=false;
        console.log(get(curr_texture_parts));
    }

    function cancel() {
        is_editing=false;
    }

    onMount(() => {
        temp_val=text;
    });
</script>

<div class="container">
    <input type="text" readonly={!is_editing ? "readonly" : ""} bind:value={temp_val} >
    {#if is_editing}
        <button on:click={cancel}> {japanese ? "キャンセル" : "Cancel"}</button> 
        <button on:click={save}> {japanese ? "保存する"  : "Save"}</button>
    {:else}
        <button on:click={edit}> {japanese ? "編集" : "Edit"}</button>
    {/if}
    <!-- <button on:click={edit}> {is_editing ? "Save" : "Edit"} </button> -->
</div>


<style>
    .container {
        display:flex;
        flex-direction: row;
        padding: 5px;
    }

</style>

<script>
    import PreviewCard from "./PreviewCard.svelte";

    export let selected_index; 
    export let pairs;
</script>

<div class="image-grid">
    {#each pairs as pair, i}
        <label class="preview-card" class:selected={selected_index===i}>
            <input type=radio bind:group={selected_index} name="option" value={i} >
            <PreviewCard texture={pair.texture} rendering={pair.rendering} info={pair.info} index={i} size=175/>
        </label>
    {/each} 
</div>


<style>
    .image-grid input[type="radio"] {
        opacity: 0;
        position: fixed;
        width:0; 
    } 

    .image-grid {
        width:100%;
        max-width:900px;
        margin:0 auto;
        text-align:left;
    }

    .preview-card {
        flex-direction: row;
        border: 1px solid grey;
        display: inline-block;
        margin:5px;
        background-color:lightblue;
    }

    .preview-card:hover {
        border: 3px solid grey;
    }

    .selected {
        border: 3px solid blue;
    }

    .selected:hover {
        border: 3px solid blue;
    }

    
</style>

<script>
  import PreviewCard from "./PreviewCard.svelte";

    export let selected_index; 
    export let pairs;
</script>

<div class="image-grid">
    {#each pairs as pair, i}
        <label class="preview-card" class:selected={selected_index===i}>
            <input type=radio bind:group={selected_index} name="option" value={i} >
            <PreviewCard texture={pair.texture} rendering={pair.rendering} info={pair.info} index={i}/>
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
        /* display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        grid-column-gap: 1rem;
        grid-row-gap: 1rem; */
        width:100%;
        max-width:900px;
        margin:0 auto;
        text-align:left;
    }

    .preview-card {
        /* display:flex;  */
        flex-direction: row;
        border: 1px solid grey;
        /* padding:5px; 
        max-width: 50%; */
        display: inline-block;
        /* height: 170px;
        width: 170px; */
        margin:5px;
        background-color:lightblue;
    }

    .preview-card:hover {
        border: 2px solid grey;
    }

    .selected {
        border: 2px solid blue;
    }

    
</style>
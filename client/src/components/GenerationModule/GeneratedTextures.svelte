
<script>
    import PreviewCard from "./PreviewCard.svelte";
    import DynamicImage from "../DynamicImage.svelte";
    import {onMount} from 'svelte';
    export let pairs;
    export let selected_texture=""; 
    export let texture_name;

    onMount(() => {
        console.log(texture_name);
    });
</script>

<div class="image-grid">
    {#each pairs as pair, i}
        <!-- <label class="preview-card" class:selected={selected_texturepaths.includes(pair.texture)}> -->
        <label class="preview-card" class:selected={selected_texture===pair.texture}>
            <input type=radio bind:group={selected_texture} name="option" value={pair.texture} >
            <div class="image"> <DynamicImage imagepath={pair.texture} size={"175px"} alt={texture_name} is_draggable={true}/> </div>
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
        margin:0 auto;
    }

    .image{
        width:100%;
        object-fit: cover;
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
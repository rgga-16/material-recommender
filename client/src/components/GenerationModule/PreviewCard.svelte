<script>
    import DynamicImage from "../DynamicImage.svelte";

    export let texture;
    export let rendering; 
    export let info; 
    export let size="200px";
    // export let index;

    let currentImage=0;
    let viewString="View texture";
    let is_selected=false;

    function switchImage() {
        if(currentImage===0) {
            currentImage = 1;
            viewString = "View rendering"
        } else {
            currentImage = 0;
            viewString = "View texture"
        }
    }

</script>

<div class="card">
    {#if rendering}
        {#if currentImage===0}
        <div class="image"> <DynamicImage imagepath={rendering} size={size} alt="Rendering"/> </div>
        {:else} 
        <div class="image"> <DynamicImage imagepath={texture} size={size} alt="Texture"/> </div>
        {/if}
        <button on:click|preventDefault={switchImage}> {viewString} </button>
    {:else}
        <div class="image"> <DynamicImage imagepath={texture} size={size} alt="Texture"/> </div>
    {/if}
    

</div>

<style>
    .card {
        display:flex; 
        flex-direction: column;
    }
    .image{
        width:100%;
        object-fit: cover;
    }

</style>

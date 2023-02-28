<script>
    export let texture;
    export let rendering; 
    // export let info; 
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
            <img src ={rendering} alt = "Rendering" />
        {:else} 
            <img src ={texture} alt = "Texture" />
        {/if}
        <button on:click|preventDefault={switchImage}> {viewString} </button>
    {:else}
        <img src ={texture} alt = "Texture" />
    {/if}
    

</div>

<style>
    .card {
        display:flex; 
        flex-direction: column;
    }
    img{
        width:100%;
        max-width: 200px;
        object-fit: cover;
    }
</style>

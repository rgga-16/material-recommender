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

{#if currentImage===0}
    <img src ={rendering} alt = "Rendering" />
{:else} 
    <img src ={texture} alt = "Texture" />
{/if}
<button on:click|preventDefault={switchImage}> {viewString} </button>

<style>
    img{
        width:100%;
        object-fit: cover;
    }

    
</style>

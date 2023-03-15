<script>
    // Based on https://codepen.io/marlasdaughter/pen/yGZZLp
    export let color_codes; 
    export let name;

    let palette;
    // const paletteWidth = palette.offsetWidth;
    // console.log(paletteWidth);
</script>

<span> {name} </span>
<div bind:this={palette} class="color-palette">
    {#each color_codes as cc, i}
        <input type="color" bind:value={cc} />
    {/each}
</div>



<style>
    .color-palette {
        display:flex; 
        flex-direction:row; 
        justify-content: left;
        width: 100%; 
        height: 100%;
    }


    input[type="color"] {
        padding: 0;
        height: 100%;
    }

    input[type="color"]::-webkit-color-swatch-wrapper {
        padding: 0;
    }
    input[type="color"]::-webkit-color-swatch {
        border: none;
    }

    input[type="color"]:hover {
        cursor:pointer;
    }


</style>
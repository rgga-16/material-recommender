<script>
    // Based on https://codepen.io/marlasdaughter/pen/yGZZLp
    export let color_codes; 
    export let name;

    let palette;
    // const paletteWidth = palette.offsetWidth;
    // console.log(paletteWidth);
</script>


<div bind:this={palette} class="color-palette">
    {#each color_codes as cc, i}
        <input type="color" value={cc} />
    {/each}
</div>
<!-- <span> {name} </span> -->

<style>
    .color-palette {
        display:flex; 
        flex-direction:row; 
        justify-content: left;
        width: 100%; 
        height: 100%;
    }


    .swatch {
        /* width: 25px; 
        height: 25px;
        border: 1px solid black; 
        margin-right: 2px; */
    }

    input[type="color"] {
        padding: 0;
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
<script>
    // Based on https://codepen.io/marlasdaughter/pen/yGZZLp
    
    export let color_codes; 
    export let name;

    let palette;

</script>

    {name}
    <div bind:this={palette} class="color-palette">
        {#each color_codes as cc, i}
            <!-- <div class="box" style="background-color: {cc}"> -->
                <input type="color" bind:value={cc} />
            <!-- </div> -->
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
/* 
    .box {
        width: 100%;
        height: 100%;
    } */


    input[type="color"] {
        /* opacity: 0;
        position: fixed;
        width:0;  */
        width: 100px;
        height: 100px;
        padding: 0; 
        border: none;
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
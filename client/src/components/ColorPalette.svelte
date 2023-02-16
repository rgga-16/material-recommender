<script>
    // Based on https://codepen.io/marlasdaughter/pen/yGZZLp
    export let color_codes; 
    export let name;
</script>

<p> {name} </p>
<div class="color-palette">
    {#each color_codes as cc}
        <input type="color" bind:value={cc} />
    {/each}
</div>

<style>
    .color-palette {
        display:flex; 
        flex-direction:row; 
        flex-grow:1 ;
        width: auto; 
        height: 100%;
    }

</style>
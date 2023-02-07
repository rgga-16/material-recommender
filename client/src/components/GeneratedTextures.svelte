
<script>
    export let rendering_texture_pairs;
</script>

<div class="image-grid">
    {#each rendering_texture_pairs as pair}
        <img class="grid-item" src={pair.rendering} alt=""/>
        <img class="grid-item" src={pair.texture} alt=""/>
    {/each} 
</div>


<style>
    .image-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        grid-gap: 10px;
    }

    .grid-item {
        width: 100%;
        height: 200px;
        object-fit: cover;
    }
</style>
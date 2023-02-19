<script>

    export let current_rendering_path;

</script>


{#if current_rendering_path}
    <h3>Current Rendering</h3>
    <img src={current_rendering_path} alt="Current rendering"/> 
{/if}

<style>
    img{
        width:50%;
        height: auto;
        object-fit: cover;
    }
</style>
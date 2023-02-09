<script>

    export let current_rendering_path;

</script>


{#if current_rendering_path}
    <img src={current_rendering_path} alt="Current rendering"/> 
{/if}

<style>
    img{
        width:70%;
        height: auto;
        object-fit: cover;
    }

</style>
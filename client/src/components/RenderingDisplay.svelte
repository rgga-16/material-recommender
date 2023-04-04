<script>
    import DynamicImage from "./DynamicImage.svelte";
    export let current_rendering_path;

    let rendering;
    function updateRendering() {
        rendering.getImage();
    }

</script>


    <h3>Current Rendering</h3>
    <div class="image">
        <DynamicImage bind:this={rendering} imagepath={current_rendering_path} alt="Current rendering" size={1000}/>
    </div>

<style>
    .image{
        width:100%;
        height: auto;
        object-fit: cover;
        border: solid 1px black; 
    }
</style>
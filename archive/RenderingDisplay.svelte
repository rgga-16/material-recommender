<script>
    import DynamicImage from "../client/src/components/DynamicImage.svelte";
    export let current_rendering_path;

    let rendering;
    function updateRendering() {
        rendering.getImage();
    }

</script>


    <h3>Current Rendering</h3>
    <div class="image">
        <DynamicImage bind:this={rendering} imagepath={current_rendering_path} alt="Current rendering" size={2000}/>
    </div>

<style>
    .image{
        width:100%;
        height: 100%;
        object-fit: cover;
        border: solid 1px black; 
    }
</style>
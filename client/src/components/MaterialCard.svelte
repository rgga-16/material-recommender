<script>
    export let material_path;
    export let material_name;
    // export let info; 
    export let index;

    let is_selected=false;

    function copyText(text) {
        console.log(text);
        navigator.clipboard.writeText(text);
    }

</script>

<p>{material_name}</p> <button on:click={() => copyText(material_name)}> Copy to clipboard </button>
<img src ={material_path} alt = {material_name} id="material-"{index}/>

<style>

    * {
        padding: 5px;
    }

    img{
        width:50%;
        object-fit: cover;
    }
</style>

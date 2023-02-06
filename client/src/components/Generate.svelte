<script>
    import {onMount} from 'svelte';

    let input_material='';
    let object_data={}; //List of names of 3D objects 

    let objs_and_parts = fetch('./get_objects_and_parts').then((x)=>x.json());

    function generate_textures() {
        // Do something with input_material
    }

    function apply_textures() {
        
    }
    
 
</script>

<div class="material_generator">
    <h2> Material Generator </h2>
    <form on:submit|preventDefault={generate_textures}>
        <input name="material_name" type="text" bind:value={input_material} required/>
        <br/>
        <div class="tab-group">
            <!-- WIP: Block for getting tabs of checkbox groups -->
            {#await objs_and_parts}
                <pre>Loading object names and their part names</pre>
            {:then data} 
                {#each Object.entries(data) as [obj,attribs]}
                    <div class="tab">
                        <input type="radio" name="css-tabs" id="tab-{obj}" checked="checked" class="tab-switch">
                        <label for="tab-{obj}" class="tab-label">{obj}</label>
                        <div class="tab-content">
                            {#each attribs.parts.names as part_name}
                                <input type="checkbox" id="checkbox-{part_name}" name="checkbox-group-{obj}">
                                <label for="checkbox-{part_name}"> {part_name} </label>
                            {/each}
                        </div>
                    </div>
                {/each}
            {/await}
        </div>
        <br/>
        <button> Generate & Transfer Material </button>
    </form>
    <form>
        <!-- This form shows a preview of up to 4 generated textures applied to the parts of the 3D models -->
    </form>

</div>



<style>
    .tab-group {
        display: flex;
        flex-direction: row;
        align-items: center;
    }
    input[type="radio"] {
        display: none;
    }
    label {
        padding: 10px 20px;
        border: 1px solid gray;
        border-radius: 5px 5px 0 0;
        cursor: pointer;
        margin-bottom: -1px;
        background-color: lightgray;
    }
    input[type="radio"]:checked + label {
        background-color: white;
    }
    .tab-content {
        border: 1px solid gray;
        border-top: none;
    }



</style>
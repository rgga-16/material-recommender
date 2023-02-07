<script>
    import {onMount} from 'svelte';
    import GeneratedTextures from './GeneratedTextures.svelte';

    let input_material='';
    let selected_object_parts=[]; 

    const objs_and_parts = fetch('./get_objects_and_parts').then((x)=>x.json());

    // let gen_texture_paths = [];
    // let rendering_paths = [];
    let rendering_texture_pairs = [];

    function handleCheckboxChange(event) {
        const checkbox = event.target; 
        checkbox.checked = event.target.checked;
    }

    async function gen_and_apply_textures(texture_str) {

        let selected_op_dict = {};

        if (selected_object_parts.length <= 0) { alert("Please select at least 1 object part"); return }

        // Insert algo to parse the selected_object_parts
        for (let i = 0; i < selected_object_parts.length; i++) {
            let splitted = selected_object_parts[i].split("-");
            let obj = splitted[0];
            let part = splitted[1];
            if(obj in selected_op_dict) {
                selected_op_dict[obj].push(part);
            } else {
                selected_op_dict[obj] = [part]; 
            }
        }
        
        const results_response = await fetch("/generate_and_transfer_textures", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                "texture_string": texture_str,
                "n":4,
                "imsize":256,
                "obj_parts_dict": selected_op_dict,
            }),
        });
        const results_json = await results_response.json();
        rendering_texture_pairs = results_json["results"];
    }
    
    // async function generate_textures(texture_str) {
    //     // Do something with input_material
    //     const gen_textures_response = await fetch("/generate_textures", {
    //         method: "POST",
    //         headers: {"Content-Type": "application/json"},
    //         body: JSON.stringify({
    //             "texture_string": texture_str,
    //             "n":4,
    //             "imsize":256
    //         }),
    //     });
    //     const gen_textures_json = await gen_textures_response.json();
    //     gen_texture_paths = gen_textures_json["generated_textures"]
    // }

    // async function apply_textures(texture_str, selected_obj_parts, texture_paths) {
    //     request_json = {
    //         "texture_string": texture_str,
    //         "obj_parts_dict": selected_obj_parts,
    //         "texture_paths": texture_paths,
    //     }
        
    //     const renderings_response = await fetch("/transfer_textures", {
    //         method: "POST",
    //         headers: {"Content-Type": "application/json"},
    //         body: JSON.stringify(request_json),
    //     });
    //     const renderings_json = await renderings_response.json();
    // }

</script>

<div class="material_generator">
    <h2> Material Generator </h2>
    <!-- <form on:submit|preventDefault={generate_textures(input_material)}> -->
    <form on:submit|preventDefault={gen_and_apply_textures(input_material)}>
        <input name="material_name" type="text" bind:value={input_material} required/>
        <br/>
        <div class="tab-group">
            <!-- WIP: Block for getting tabs of checkbox groups -->
            {#await objs_and_parts}
                <pre>Loading object names and their part names</pre>
            {:then data} 
                {#each Object.entries(data) as [obj_name,attribs]}
                    <div class="tab">
                        <input type="radio" name="css-tabs" id="tab-{obj_name}" checked="checked" class="tab-switch">
                        <label for="tab-{obj_name}" class="tab-label">{obj_name}</label>
                        <div class="tab-content">
                            {#each attribs.parts.names as part_name}
                                <input type="checkbox" bind:group={selected_object_parts} id="checkbox-{obj_name}-{part_name}" name="checkbox-group-{obj_name}" value="{obj_name}-{part_name}" >
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
    {#if rendering_texture_pairs}
        <form>
            <GeneratedTextures rendering_texture_pairs= {rendering_texture_pairs} />
        </form>
    {/if}
    
        <!-- This form shows a preview of up to 4 generated textures applied to the parts of the 3D models -->
    

</div>



<style>
    .tab-group {
        display: flex;
        flex-direction: column;
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
<script>
    import {onMount} from 'svelte';
    import GeneratedTextures from './GeneratedTextures.svelte';
    import {curr_rendering_path} from '../stores.js';
    

    let input_material='';
    let selected_object_parts=[]; 

    const objs_and_parts = fetch('./get_objects_and_parts').then((x)=>x.json());

    let rendering_texture_pairs=[];

    let selected_index;

    async function gen_and_apply_textures(texture_str) {
        rendering_texture_pairs=[];

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
                "imsize":448,
                "obj_parts_dict": selected_op_dict,
            }),
        });
        const results_json = await results_response.json();
        rendering_texture_pairs = results_json["results"];
    }

    async function apply_to_curr_rendering(index) {

        if(index==undefined) {
            alert("Please select one of the options"); 
            return;
        }
        let selected_render_texture_pair = rendering_texture_pairs[index];

        let selected_rendering_path = selected_render_texture_pair.rendering; 
        let selected_texture_path = selected_render_texture_pair.texture; 
        let selected_rendering_info = selected_render_texture_pair.info; 
        let selected_info_path = selected_render_texture_pair.info_path;

        const response = await fetch("/apply_to_current_rendering", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                "rendering_path": selected_rendering_path,
                "texture_parts":selected_rendering_info,
                "textureparts_path": selected_info_path
            }),
        });

        const json = await response.json();

        curr_rendering_path.set(json["rendering_path"]);

    }

</script>

<div class="material_generator">
    <h2> Material Generator </h2>

    <form on:submit|preventDefault={gen_and_apply_textures(input_material)}>
        <input name="material_name" type="text" bind:value={input_material} placeholder="Type in a material texture..." required/>
        <button> Generate Material </button>
        <br/>

            {#await objs_and_parts}
                <pre>Loading object names and their part names</pre>
            {:then data} 
                {#each Object.entries(data) as [obj_name,attribs]}
                    <div class="tab">
                        <input type="radio" name="css-tabs" id="tab-{obj_name}" checked="checked" class="tab-switch">
                        <label for="tab-{obj_name}" class="tab-label">{obj_name}</label>

                        <div class="checkbox-group">
                            {#each attribs.parts.names as part_name}
                                <div class="checkbox-item">
                                    <label for="checkbox-{part_name}"> 
                                        <input type="checkbox" bind:group={selected_object_parts} id="checkbox-{obj_name}-{part_name}" 
                                        name="checkbox-group-{obj_name}" value="{obj_name}-{part_name}" >
                                        {part_name} 
                                    </label>
                                </div>
                            {/each}
                        </div>
                    </div>
                    
                {/each}
            {/await}

        <br/>
        
    </form>
    {#if rendering_texture_pairs.length > 0}
        <!-- <div class='carousel'>
            <div class="carousel-item">

            </div>

        </div> -->
        <form on:submit|preventDefault={apply_to_curr_rendering(selected_index)} >
            <GeneratedTextures pairs= {rendering_texture_pairs} bind:selected_index={selected_index} />
            <button> Apply to rendering </button>
        </form>
    {/if}
    
</div>

<style>
    /* .carousel {
        display:flex;
        flex-wrap:nowrap;
        overflow-x:hidden;
    }

    .carousel-item{
        min-width:100%;
        flex:0 0 auto; 
        margin-right:1rem; 
    } */

    .tab {
        border: 1px solid gray;
    }

    .material_generator {
        display: flex;
        flex-direction: column;
        width:100%;
    }

    input[type="radio"] {
        display: none;
    }
    
    label {
        padding: 5px;
        /* border: 1px solid gray;
        border-radius: 5px 5px 0 0;
        margin-bottom: -1px;
        background-color: lightgray; */
    }
    input[type="radio"]:checked + label {
        background-color: white;
    }
    .checkbox-group {
        /* display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        grid-column-gap: 5px;
        grid-row-gap: 5px; */
        width:100%;
        max-width:900px;
        margin:0 auto;
        text-align:left;
    }
    .checkbox-item {
        /* padding:5px; 
        max-width: 50%; */
        display: inline-block;
        /* height: 170px;
        width: 170px; */
        margin:5px;
        background-color:lightblue;
    }



</style>






    

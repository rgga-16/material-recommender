<script>
    import {onMount} from 'svelte';
    import { Circle } from 'svelte-loading-spinners';

    import GeneratedRenderings from './GeneratedRenderings.svelte';
    import GeneratedTextures from './GeneratedTextures.svelte';
    import RefineTexture from './RefineTexture.svelte';
    import {curr_rendering_path} from '../../stores.js';

    let input_material='';

    let selected_object_parts=[]; 
    let objs_and_parts = {}
    let selected_obj_parts_dict = {}

    let rendering_texture_pairs=[];

    let is_loading;
    let generated_textures = [];
    let selected_textures = [];

    let selected_index;

    onMount(async () => {
        const obj_and_part_resp= await fetch('./get_objects_and_parts');
        const obj_and_part_json = await obj_and_part_resp.json(); 
        objs_and_parts = obj_and_part_json;
    }); 

    async function generate_textures(texture_str) {
        is_loading=true; 
        generated_textures=[];
        const results_response = await fetch("/generate_textures", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                "texture_string": texture_str,
                "n":4,
                "imsize":448,
            }),
        });
        const results_json = await results_response.json();
        generated_textures = results_json["results"];
        is_loading=false;
    }

    async function apply_textures() {
        rendering_texture_pairs=[];
        selected_obj_parts_dict = {};
        is_loading=true;

        if (selected_object_parts.length <= 0) { alert("Please select at least 1 object part"); return }

        for (let i = 0; i < selected_object_parts.length; i++) {
            let splitted = selected_object_parts[i].split("-");
            let obj = splitted[0];
            let part = splitted[1];
            if(obj in selected_obj_parts_dict) {
                selected_obj_parts_dict[obj].push(part);
            } else {
                selected_obj_parts_dict[obj] = [part]; 
            }
        }

        const results_response = await fetch("/apply_textures", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                "obj_parts_dict": selected_obj_parts_dict,
                "selected_texturepaths":selected_textures,
                "texture_string":input_material
            }),
        });
        const results_json = await results_response.json();
        rendering_texture_pairs = results_json["results"];
        is_loading=false;
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

    const n_pages = 4;
    let current_page = 0;

    function next_page() {
        current_page+=1;
        if (current_page >= n_pages) {
            current_page=n_pages-1;
        }
    }

    function prev_page() {
        current_page-=1;
        if(current_page < 0){
            current_page=0;
        }
    }


</script>

<div class="material_generator">
    <header> Material Generator </header>

    <div class="page" class:hidden={current_page!=0} id="generate_materials">
        <form on:submit|preventDefault={generate_textures(input_material)}>
            <input name="material_name" type="text" bind:value={input_material} placeholder="Type in a material texture..." required/>
            <button> Generate Material </button>
        </form>
        {#if generated_textures.length > 0}
                <GeneratedTextures pairs= {generated_textures} bind:selected_texturepaths={selected_textures}/>
                <p> {selected_textures.length}/4 textures selected. {#if selected_textures.length<=0} Please select at least 1 texture map to proceed.{/if}</p>
        {:else if is_loading==true}
            <div class="images-placeholder">
                <Circle size="60" color="#FF3E00" unit="px" duration="1s" />
            </div>
        {:else}
            <div class="images-placeholder">
                <pre>No material textures generated yet.</pre>
            </div>
        {/if}
        <div class="carousel-nav-btns">
            {#if selected_textures.length > 0}
                <button on:click|preventDefault={()=>next_page()}> Next </button>
            {/if}
        </div>
    </div>

    <div class="page" class:hidden={current_page!=1} id="apply_textures">
        <form on:submit|preventDefault={()=>apply_textures()}>
            <h4> Apply textures to rendering</h4>
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
            <button> Apply textures </button>
        </form>
        {#if rendering_texture_pairs.length > 0}
                <GeneratedRenderings pairs= {rendering_texture_pairs} bind:selected_index={selected_index} />
                {#if selected_index!=undefined}
                    <p> Rendering #{selected_index} selected. </p>
                {:else }
                    <p> Please select a rendering to proceed.</p>
                {/if}
        {:else if is_loading==true}
            <div class="images-placeholder">
                <Circle size="60" color="#FF3E00" unit="px" duration="1s" />
            </div>
        {:else}
            <div class="images-placeholder">
                <pre>No renderings generated yet.</pre>
            </div>
        {/if}
        
        <div class="carousel-nav-btns">
            <button on:click|preventDefault={()=>prev_page()}> Prev </button>
            {#if selected_index!=undefined}
                <button on:click|preventDefault={()=>next_page()}> Next </button>
            {/if}
        </div>
    </div>

    <div class="page" class:hidden={current_page!=2} id="refine_textures">
        {#if selected_index!=undefined && rendering_texture_pairs.length > 0}
            <RefineTexture bind:selected_index={selected_index} 
            bind:rendering_texture_pairs={rendering_texture_pairs} 
            objs_and_parts={objs_and_parts} 
            bind:selected_objs_and_parts_dict={selected_obj_parts_dict}/>
        {/if}
        
        <div class="carousel-nav-btns">
            <button on:click|preventDefault={()=>prev_page()}> Previous </button>
            <!-- <button on:click|preventDefault={()=>next_page()}> Next </button> -->
            <button on:click|preventDefault={()=>next_page()}> Next </button>
        </div>
    </div>

    

</div>

<style>


    .tab {
        border: 1px solid gray;
    }

    .material_generator {
        display: flex;
        align-items:center;
        justify-content:center;
        flex-direction: column;
        width:100%;
        height: 100%; 
        background: white; 
        overflow: hidden;
        text-align: center;
    }
    
    .material_generator div.page{
        text-align: center;
        align-items: center;
        justify-content: center;
        min-height:800px;
        width:100%;
        height: 100%; 
    }   

    .material_generator .page.hidden{
        display:none;
    }

    .material_generator .page .carousel-nav-btns {
        padding:5px;
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
    
    .images-placeholder {
        width: 100%;
        height: 500px;
        border: 1px dashed black;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
    }



</style>



<!-- async function gen_and_apply_textures(texture_str) {
        
    rendering_texture_pairs=[];
    let selected_obj_parts_dict = {};

    if (selected_object_parts.length <= 0) { alert("Please select at least 1 object part"); return }
    for (let i = 0; i < selected_object_parts.length; i++) {
        let splitted = selected_object_parts[i].split("-");
        let obj = splitted[0];
        let part = splitted[1];
        if(obj in selected_obj_parts_dict) {
            selected_obj_parts_dict[obj].push(part);
        } else {
            selected_obj_parts_dict[obj] = [part]; 
        }
    }
    
    const results_response = await fetch("/generate_and_transfer_textures", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            "texture_string": texture_str,
            "n":4,
            "imsize":448,
            "obj_parts_dict": selected_obj_parts_dict,
        }),
    });
    const results_json = await results_response.json();
    rendering_texture_pairs = results_json["results"];
} -->


    

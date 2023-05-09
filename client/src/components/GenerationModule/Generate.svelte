<script>
    import {onMount} from 'svelte';
    import { Circle } from 'svelte-loading-spinners';
    import NumberSpinner from "svelte-number-spinner";
    import GeneratedRenderings from './GeneratedRenderings.svelte';
    import GeneratedTextures from './GeneratedTextures.svelte';
    import RefineTexture from './RefineTexture.svelte';
    import {curr_rendering_path} from '../../stores.js';
    import {curr_texture_parts} from '../../stores.js';
	import {curr_textureparts_path} from '../../stores.js';
    import {actions_panel_tab} from '../../stores.js';
    import {generate_tab_page} from '../../stores.js';

    export let onCallUpdateCurrentRendering
    function callUpdateCurrentRendering() {
        onCallUpdateCurrentRendering();
    }

    let input_material='';

    let selected_object_parts=[]; 
    let objs_and_parts = {}
    let selected_obj_parts_dict = {}

    let rendering_texture_pairs=[];

    let is_loading;
    let generated_textures = [];
    let selected_textures = [];

    let selected_index;

    let n_textures = 8;

    onMount(async () => {
        const obj_and_part_resp= await fetch('./get_objects_and_parts');
        const obj_and_part_json = await obj_and_part_resp.json(); 
        objs_and_parts = obj_and_part_json;
    }); 

    export async function generate_textures(texture_str) {
        input_material=texture_str;
        is_loading=true; 
        generated_textures=[];
        const results_response = await fetch("/generate_textures", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                "texture_string": texture_str,
                "n":n_textures,
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
        

        if (selected_object_parts.length <= 0) { alert("Please select at least 1 object part"); return }
        is_loading=true;
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
        curr_texture_parts.set(await json["texture_parts"]);
		curr_textureparts_path.set(await json["textureparts_path"]);

        callUpdateCurrentRendering();
    }

    const n_pages = 4;

    let current_page = 0;
    generate_tab_page.subscribe(value=> {
        current_page=value;
    });

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

    let active_obj_id=0;
    function switchObjectTab(id) {
        active_obj_id=id;
    }

    //This function reverts back to the first page of the Generation module.
    export function reset_page() {
        current_page=0;
        generate_tab_page.set(0);

        generated_textures=[];
        rendering_texture_pairs=[];
        selected_textures = [];
        switchObjectTab(0);
        selected_object_parts=[];
        selected_index=undefined;

    }

</script>

<div class="material_generator">
    <header> Material Generator </header>

    <div class="page" class:hidden={current_page!=0} id="generate_materials">
        <form on:submit|preventDefault={generate_textures(input_material)}>
            <div class="row">
                <input name="material_name" type="text" bind:value={input_material} placeholder="Type in a material texture..." required/>
                <button> Generate Material </button>
            </div>
            
            <div >
                <span> No. of texture maps: </span>
                <NumberSpinner bind:value={n_textures} min={1} max={20} step=1/>
            </div>

        </form>
        {#if generated_textures.length > 0}
                <p> Texture map results for: {input_material}</p>
                <GeneratedTextures pairs= {generated_textures} bind:selected_texturepaths={selected_textures}/>
                <p> {selected_textures.length}/{n_textures} textures selected. {#if selected_textures.length<=0} Please select at least 1 texture map to proceed.{/if}</p>
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
            {#if generated_textures.length > 0}
                <button disabled={selected_textures.length<=0} on:click|preventDefault={()=>next_page()}> Next </button>
            {/if}
        </div>
    </div>

    <div class="page" class:hidden={current_page!=1} id="apply_textures">
        <form on:submit|preventDefault={()=>apply_textures()}>
            <h4> Apply textures to rendering</h4>
            {#await objs_and_parts}
                <pre>Loading object names and their part names</pre>
            {:then data} 
                <div class="w3-bar w3-grey tabs">
                    {#each Object.entries(data) as [obj_name, attribs],i}
                        <button class="w3-bar-item w3-button tab-btn" class:active={active_obj_id===i} on:click|preventDefault={()=>switchObjectTab(i)}> {obj_name} </button>
                    {/each}
                </div>

                {#each Object.entries(data) as [obj_name,attribs], i}
                    <div class="tab-content" class:active={active_obj_id===i}>
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
            <button on:click|preventDefault={()=>prev_page()}> Back </button>
            <button disabled={!(selected_index!=undefined && rendering_texture_pairs.length > 0)} on:click|preventDefault={()=>next_page()}> Next </button>
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
            <button on:click|preventDefault={()=>prev_page()}> Back </button>
            <button on:click|preventDefault={()=>apply_to_curr_rendering(selected_index)}> Apply to current rendering </button>
        </div>
    </div>

    

</div>

<style>

    .tab-btn {
        height:100%;
    }

	.tab-btn.active {
		background-color: rgb(89, 185, 218);
	}

    .tab-btn.active:hover {
		background-color: rgb(89, 185, 218);
	}

	.tab-content {
		display: none;
	}

    .tab-content.active {
		display: flex;
        flex-direction: row;
        height: 100%;
        width:100%;
        padding: 5px;
        overflow: auto;
	}

    .material_generator {
        display: flex;
        align-items:center;
        justify-content:center;
        flex-direction: column;
        width:100%;
        height: 100%; 
        /* overflow: hidden; */
        text-align: center;
    }

    .row {
        display:flex; 
        flex-direction: row;
        align-items: center;
        justify-content: center;
        gap: 5px;
    }

    .column {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 5px;
    }

    
    .material_generator div.page{
        text-align: center;
        align-items: center;
        justify-content: center;
        overflow:auto;
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
    }

    input[type="radio"]:checked + label {
        background-color: white;
    }

    .checkbox-group {
        width:100%;
        max-width:900px;
        margin:0 auto;
        text-align:left;
    }
    .checkbox-item {
        display: inline-block;
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

<!-- OLD CODE BELOW-->
    

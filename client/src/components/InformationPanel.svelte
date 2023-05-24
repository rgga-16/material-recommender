<script>
    import { Circle } from 'svelte-loading-spinners';
    // import {createComponent} from 'svelte';
    import {get} from 'svelte/store';
    import {curr_texture_parts} from '../stores.js';
    import {selected_part_name} from '../stores.js';
    import {selected_obj_name} from '../stores.js';
    import {selected_objs_and_parts} from '../stores.js';
    import TexturePart from './TexturePart.svelte';
    import PartPairs from './PartPairs.svelte';
    import {onMount} from 'svelte';

    import {actions_panel_tab} from '../stores.js';
    import {generate_tab_page} from '../stores.js';

    import {information_panel_tab} from '../stores.js';
    
    let current_texture_parts = get(curr_texture_parts);

    let selected_part=null; 
    selected_part_name.subscribe(value => {
		selected_part = value;
	});

    let selected_object=null;
    selected_obj_name.subscribe(value => {
        selected_object = value;
    });

    let sel_objs_and_parts = null; 
    selected_objs_and_parts.subscribe(value => {
        sel_objs_and_parts = value;
    });
    
    let objects = Object.keys(current_texture_parts);

    let selected_obj = objects[0];
    let selected_parts = Object.keys(current_texture_parts[selected_obj]);
    
    let textureparts = [];
    let texturepart_infos = [];
    let partpairs = [];
    let partpairs_infos = [];

    let is_loading=false;
    let activeTab;

    information_panel_tab.subscribe(value => {
        activeTab = value;
    });

    function switchTab(tab) {
        information_panel_tab.set(tab);
    }

    export function displayTexturePart() {
        let textureparts=[];
        const textureparts_div = document.getElementById("texture-part-details");
        textureparts_div.innerHTML='';

        for(let i=0; i < sel_objs_and_parts.length; i++) {
            let selected_part_parent = sel_objs_and_parts[i].parent; 
            let selected_part = sel_objs_and_parts[i].name;
            // let selected_part_material = sel_objs_and_parts[i].model.children[0].material;
            
            let mat_name = current_texture_parts[selected_part_parent][selected_part]["mat_name"];
            let material_url = current_texture_parts[selected_part_parent][selected_part]["mat_image_texture"];
            let material_finish = current_texture_parts[selected_part_parent][selected_part]["mat_finish"];

            let material_color = null;
            if(current_texture_parts.hasOwnProperty('mat_color')) {
                material_color = current_texture_parts[selected_part_parent][selected_part]["mat_color"];
            }
            let texturepart = new TexturePart({
                target: textureparts_div,
                props: {
                    index:i,
                    part_parent_name: selected_part_parent,
                    part_name: selected_part,
                    material_name: mat_name,
                    material_url: material_url,
                    material_finish: material_finish,
                    material_color: material_color,
                }
            });
            textureparts.push(texturepart);
            textureparts=textureparts;
        }

    }

    function displayTextureParts() {
        textureparts=[];
        selected_parts = Object.keys(current_texture_parts[selected_obj]);
        const textureparts_div = document.getElementById("texture-parts");
        textureparts_div.innerHTML='';
        for (let i = 0; i < selected_parts.length; i++) {
            let texturepart = new TexturePart({
                target: document.getElementById("texture-parts"),
                props: {
                    part_name: selected_parts[i],
                    material_name: current_texture_parts[selected_obj][selected_parts[i]]["mat_name"],
                    material_url: current_texture_parts[selected_obj][selected_parts[i]]["mat_image_texture"],
                    material_finish: current_texture_parts[selected_obj][selected_parts[i]]["mat_finish"],
                }
            });
            textureparts.push(texturepart);
        }
    }

    function updatePartPairs() {
        
        selected_parts = Object.keys(current_texture_parts[selected_obj]);
        partpairs_infos = [];

        for (let i = 0; i < selected_parts.length; i++) {
            let child_part = selected_parts[i];
            if (current_texture_parts[selected_obj][child_part]["parents"].length > 0) {
                for (let j = 0; j < current_texture_parts[selected_obj][child_part]["parents"].length; j++) {
                    let parent_part = current_texture_parts[selected_obj][child_part]["parents"][j];
                    let partpair_info = {
                        "child_part": child_part,
                        "child_mat_name": current_texture_parts[selected_obj][child_part]["mat_name"],
                        "child_mat_url": current_texture_parts[selected_obj][child_part]["mat_image_texture"],
                        "child_mat_finish": current_texture_parts[selected_obj][child_part]["mat_finish"],
                        "parent_part": parent_part,
                        "parent_mat_name": current_texture_parts[selected_obj][parent_part]["mat_name"],
                        "parent_mat_url": current_texture_parts[selected_obj][parent_part]["mat_image_texture"],
                        "parent_mat_finish": current_texture_parts[selected_obj][parent_part]["mat_finish"],
                    }
                    partpairs_infos.push(partpair_info);
                }
            }
        }

    }

    function displayPartPairs() {
        partpairs=[];
        const partpairs_div = document.getElementById("part-pairs");
        partpairs_div.innerHTML='';
        for (let i = 0; i < partpairs_infos.length; i++) {
            let partpair = new PartPairs({
                target: partpairs_div,
                props: {
                    obj: selected_obj,
                    child_part: partpairs_infos[i]["child_part"],
                    child_mat_name: partpairs_infos[i]["child_mat_name"],
                    child_mat_finish: partpairs_infos[i]["child_mat_finish"],
                    child_mat_url: partpairs_infos[i]["child_mat_url"],

                    parent_part: partpairs_infos[i]["parent_part"],
                    parent_mat_name: partpairs_infos[i]["parent_mat_name"],
                    parent_mat_finish: partpairs_infos[i]["parent_mat_finish"],
                    parent_mat_url: partpairs_infos[i]["parent_mat_url"],
                }
            });
            partpairs.push(partpair);
        }
    }

    function updateAndDisplayPartPairs() {
        updatePartPairs();
        displayPartPairs();
    }

    export async function updatePartInformation() {
        is_loading=true;
        selected_parts = Object.keys(current_texture_parts[selected_obj]);
        updateAndDisplayPartPairs();
        displayTextureParts();

        for (let i = 0; i < textureparts.length; i++) {
            textureparts[i].updateImage();
        }
        // updateAndDisplayPartPairs();
        
        for (let j = 0; j < partpairs.length; j++) {
            partpairs[j].updateImages();
        }
        is_loading=false;
    }
    curr_texture_parts.subscribe(value => {
		current_texture_parts = value;
	});
    onMount(async () => {
        updateAndDisplayPartPairs();
        displayTextureParts();
        console.log(current_texture_parts);
    });

</script>

<div class="information-panel">
    <div class="w3-bar w3-grey tabs">
        <!-- <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='information'} on:click={()=>switchTab('information')} id="information-btn">Information</button>
        <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='feedback'} on:click={()=>switchTab('feedback')}  id="feedback-btn">Feedback</button> -->
        <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='details'} on:click={()=>switchTab('details')}  id="details-btn">Details</button>
    </div>

    <!-- <div class='tab-content'  class:active={activeTab==='information'} id="information">
        <h3> Rendering Information </h3>
        <select bind:value={selected_obj} on:change={() => displayTextureParts()}>
            {#each objects as obj}
                <option value={obj}>
                    {obj}
                </option>
            {/each}
        </select>
        {#if is_loading}
            <div class="images-placeholder">
                <Circle size="60" color="#FF3E00" unit="px" duration="1s" />
                <div id="texture-parts"> </div>
            </div>
        {:else}
            <div id="texture-parts"> </div>
        {/if}
    </div>  -->

    <!-- <div class='tab-content' class:active={activeTab==='feedback'} id="feedback">   
        <h3> Feedback </h3>
        <select bind:value={selected_obj} on:change={() => updateAndDisplayPartPairs()}>
            {#each objects as obj}
                <option value={obj}>
                    {obj}
                </option>
            {/each}
        </select>
        {#if is_loading}
            <div class="images-placeholder">
                <Circle size="60" color="#FF3E00" unit="px" duration="1s" />
            </div>
            <div id="part-pairs"> </div>
        {:else}
            <div id="part-pairs"> </div>
        {/if}
    </div> -->

    <div class="tab-content" class:active={activeTab==='details'} id="details">
        <h3> Object Details </h3>
        {#if sel_objs_and_parts.length > 0}
            <div id="texture-part-details">  </div>
        {:else }
            <div class="images-placeholder">
                No object selected. Please select an object in the 3D View.
            </div>
            <div id="texture-part-details"> </div>
        {/if}
    </div>
</div>

<style>

    .information-panel {
        display: flex;
        align-items:center;
        justify-content:center;
        flex-direction: column;
        width:100%;
        height: 100%; 
        text-align: center;
    }
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
        flex-direction: column;
        height: 100%;
        width:100%;
        padding: 5px;
        overflow: auto; 
    }

    .images-placeholder {
        width: 100%;
        height: 50%;
        border: 1px dashed black;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
    }
</style>

<!-- Old Code -->

<!-- {#each selected_parts as child_part, i}
        {#if current_texture_parts[selected_obj][child_part]["parents"].length > 0}
            {#each current_texture_parts[selected_obj][child_part]["parents"] as parent_part, j}
                <PartPairs bind:this={partpairs[i*j]} 
                    bind:obj={selected_obj} 
                    bind:child_part={child_part} 
                    bind:child_mat_name={current_texture_parts[selected_obj][child_part]['mat_name']}
                    bind:child_mat_finish={current_texture_parts[selected_obj][child_part]['mat_finish']}
                    bind:child_mat_url={current_texture_parts[selected_obj][child_part]['mat_image_texture']}

                    bind:parent_part={parent_part} 
                    bind:parent_mat_name={current_texture_parts[selected_obj][parent_part]['mat_name']}
                    bind:parent_mat_finish={current_texture_parts[selected_obj][parent_part]['mat_finish']}
                    bind:parent_mat_url={current_texture_parts[selected_obj][parent_part]['mat_image_texture']} 
                />                 
            {/each}
        {/if}
    {/each} -->
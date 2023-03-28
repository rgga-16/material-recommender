<script>
    import { Circle } from 'svelte-loading-spinners';
    import {get} from 'svelte/store';
    import {curr_texture_parts} from '../stores.js';
    import TexturePart from './TexturePart.svelte';
    import PartPairs from './PartPairs.svelte';

    import {information_panel_tab} from '../stores.js';
    
    let current_texture_parts = get(curr_texture_parts);
    
    let objects = Object.keys(current_texture_parts);

    let selected_obj = objects[0];
    let selected_parts = Object.keys(current_texture_parts[selected_obj]);

    let textureparts = [];
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

    function updatePartPairs() {
        selected_parts = Object.keys(current_texture_parts[selected_obj]);
        partpairs_infos = [];

        for (let i = 0; i < selected_parts.length; i++) {
            let child_part = selected_parts[i];
            if (current_texture_parts[selected_obj][child_part]["parents"].length > 0) {
                for (let j = 0; j < current_texture_parts[selected_obj][child_part]["parents"].length; j++) {
                    let parent_part = current_texture_parts[selected_obj][child_part]["parents"][j];
                    let partpair_info = {
                        "parent_part": parent_part,
                        "child_part": child_part,
                        "parent_part_path": current_texture_parts[selected_obj][parent_part]["path"],
                        "child_part_path": current_texture_parts[selected_obj][child_part]["path"]
                    }
                    partpairs_infos.push(partpair_info);
                }
            }
        }

    }

    export async function updatePartInformation() {

        is_loading=true;
        selected_parts = Object.keys(current_texture_parts[selected_obj]);
        
        for (let i = 0; i < textureparts.length; i++) {
            textureparts[i].updateImage();
        }

        updatePartPairs();
        
        for (let j = 0; j < partpairs.length; j++) {
            partpairs[j].updateImages();
        }
        is_loading=false;
    }
    
    curr_texture_parts.subscribe(value => {
		current_texture_parts = value;
	});
    updatePartPairs();



    
</script>

<div class="information-panel">
    <div class="w3-bar w3-grey tabs">
        <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='information'} on:click={()=>switchTab('information')} id="information-btn">Information</button>
        <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='feedback'} on:click={()=>switchTab('feedback')}  id="feedback-btn">Feedback</button>
    </div>

    <div class='tab-content'  class:active={activeTab==='information'} id="information">
        <h3> Rendering Information </h3>

        <select bind:value={selected_obj} on:change={() => updatePartInformation()}>
            {#each objects as obj}
                <option value={obj}>
                    {obj}
                </option>
            {/each}
        </select>

        <!-- <div class="image-grid"> -->
        {#if is_loading}
            <div class="images-placeholder">
                <Circle size="60" color="#FF3E00" unit="px" duration="1s" />
            </div>
        {:else}
            {#each selected_parts as part,i}
                <TexturePart bind:this={textureparts[i]} 
                    bind:part_name ={part} 
                    bind:material_name={current_texture_parts[selected_obj][part]['mat_name']} 
                    bind:material_finish={current_texture_parts[selected_obj][part]['mat_finish']} 
                    bind:material_url={current_texture_parts[selected_obj][part]['mat_image_texture']} 
                />
            {/each}
        {/if}
            
        <!-- </div> -->

    </div> 

    <div class='tab-content' class:active={activeTab==='feedback'} id="feedback">   
        <h3> Feedback </h3>
        <select bind:value={selected_obj} on:change={() => updatePartInformation()}>
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
        {:else}
            {#each partpairs_infos as partpair_info, i}
                <PartPairs bind:this={partpairs[i]} 
                    bind:obj={selected_obj} 
                    bind:child_part={partpair_info.child_part} 
                    bind:child_mat_name={current_texture_parts[selected_obj][partpair_info.child_part]['mat_name']}
                    bind:child_mat_finish={current_texture_parts[selected_obj][partpair_info.child_part]['mat_finish']}
                    bind:child_mat_url={current_texture_parts[selected_obj][partpair_info.child_part]['mat_image_texture']}

                    bind:parent_part={partpair_info.parent_part} 
                    bind:parent_mat_name={current_texture_parts[selected_obj][partpair_info.parent_part]['mat_name']}
                    bind:parent_mat_finish={current_texture_parts[selected_obj][partpair_info.parent_part]['mat_finish']}
                    bind:parent_mat_url={current_texture_parts[selected_obj][partpair_info.parent_part]['mat_image_texture']}
                />
            {/each}
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
        overflow: hidden;
        text-align: center;
    }
    .tab-btn {
        height:100%;
    }

    .tab-btn.active {
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
        height: 500px;
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
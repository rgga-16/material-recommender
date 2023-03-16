<script>
    import {get} from 'svelte/store';
    import {curr_texture_parts} from '../stores.js';
    import TexturePart from './TexturePart.svelte';
    import PartPairs from './PartPairs.svelte';
    
    let current_texture_parts = get(curr_texture_parts);
    // export let current_texture_parts;
    
    let objects = Object.keys(current_texture_parts);
    console.log(objects);

    let selected_obj = objects[0];
    // let current_texture_parts[selected_obj] = current_texture_parts[selected_obj];
    let selected_parts = Object.keys(current_texture_parts[selected_obj]);

    let textureparts = [];

    let is_loading=false;
    let activeTab = 'tab1-content';

    function switchTab(tab) {
        activeTab = tab;
    }

    
    export function loadParts() {
        // current_texture_parts[selected_obj] = current_texture_parts[selected_obj];
        selected_parts = Object.keys(current_texture_parts[selected_obj]);

        for (let i = 0; i < textureparts.length; i++) {
            textureparts[i].updateImage();
        }
    }

    
    curr_texture_parts.subscribe(value => {
		current_texture_parts = value;
	});

    
</script>

<div class="information-panel">
    <div class="w3-bar w3-grey tabs">
        <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='tab1-content'} on:click={()=>switchTab('tab1-content')} id="tab1-btn">Information</button>
        <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='tab2-content'} on:click={()=>switchTab('tab2-content')}  id="tab2-btn">Feedback</button>
    </div>

    <div class='tab-content'  class:active={activeTab==='tab1-content'} id="tab1-content">
        <h3> Rendering Information </h3>

        <select bind:value={selected_obj} on:change={() => loadParts()}>
            {#each objects as obj}
                <option value={obj}>
                    {obj}
                </option>
            {/each}
        </select>

        <div class="image-grid">
            {#each selected_parts as part,i}
                <TexturePart bind:this={textureparts[i]} 

                    bind:part_name ={part} 
                    bind:material_name={current_texture_parts[selected_obj][part]['mat_name']} 
                    bind:material_finish={current_texture_parts[selected_obj][part]['mat_finish']} 
                    bind:material_url={current_texture_parts[selected_obj][part]['mat_image_texture']} 
                />
            {/each}
        </div>

    </div> 

    <div class='tab-content' class:active={activeTab==='tab2-content'} id="tab2-content">   
        <h3> Feedback </h3>

        <select bind:value={selected_obj} on:change={() => loadParts()}>
            {#each objects as obj}
                <option value={obj}>
                    {obj}
                </option>
            {/each}
        </select>

        <div class="image-grid">
            {#each selected_parts as child_part}
                {#if current_texture_parts[selected_obj][child_part]["parents"].length > 0}
                    {#each current_texture_parts[selected_obj][child_part]["parents"] as parent_part}
                        <PartPairs obj={selected_obj} object_info={current_texture_parts[selected_obj]} child_part={child_part} parent_part={parent_part} />
                    {/each}
                {/if}
            {/each}
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
  
	.tab-content {
		display: none;
	}
  
	.tab-content.active {
		display: block;
        padding: 1rem;
        background-color: lightgray;
	}

    .image-grid {
        display:flex; 
        flex-direction: column;
        overflow-y: scroll;
        padding: 5px;
    }
</style>
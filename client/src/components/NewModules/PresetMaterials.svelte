<script> 
    import {onMount} from 'svelte';
    import { Circle } from 'svelte-loading-spinners';
    import NumberSpinner from "svelte-number-spinner";

    import {curr_rendering_path} from '../../stores.js';
    import {curr_texture_parts} from '../../stores.js';
	import {curr_textureparts_path} from '../../stores.js';
    import {generate_tab_page} from '../../stores.js';
    import {generated_texture_name} from '../../stores.js';
    import { get } from 'svelte/store';
    import {action_history} from '../../stores.js';
    import { threed_display_global } from '../../stores.js';

    import {transferred_texture_url} from '../../stores.js';
    import {transferred_textureimg_url} from '../../stores.js';
    import {transferred_texture_name} from '../../stores.js';
    import {in_japanese} from '../../stores.js';

    import {addToHistory} from '../../main.js';
    import {translate} from '../../main.js';
    import {getImage} from '../../main.js';
    import {isDict, dictToString} from '../../main.js';

    import DynamicImage from "../DynamicImage.svelte";

    let preset_materials = {};

    let history; 
    action_history.subscribe(value => {
        history = value;
    });

    let activeMaterialTab = 'wood'; 
    function setActiveMaterialTab(tab) {
        activeMaterialTab = tab;
    }

    async function loadPresetMaterials() {
        let response = await fetch('/get_preset_materials');
		let data = await response.json();

        
        return data["preset_material_paths"];
    }

    onMount(async function () {
        preset_materials = await loadPresetMaterials();
        console.log("Preset materials: ", preset_materials);
    });


</script>

<div id="material_library">
    <!-- <div class="w3-bar w3-grey tabs">

        <button class='w3-bar-item w3-button tab-btn' class:active={activeMaterialTab==='wood'} on:click={()=>setActiveMaterialTab('wood')} id="wood-btn">
            Wood
        </button>
        
        <button class='w3-bar-item w3-button tab-btn' class:active={activeMaterialTab==='metal'} on:click={()=>setActiveMaterialTab('metal')} id="metal-btn">
            Metal
        </button>


    </div> -->

    <div class="tab-content" class:active={activeMaterialTab==='wood'} id="wood">
        <div class="image-grid">
            {#each Object.entries(preset_materials) as [name,path]}
                <div class="column center">
                    <strong> {name} </strong>
                    <DynamicImage imagepath={path} size={"200px"} alt={name} is_draggable={true}/>
                </div>
            {/each}
            <!-- <DynamicImage imagepath={"preset_materials/wood-01-1k/wood 01 Diffuse.jpg"} imagesource={"preset_materials/wood-01-1k/wood 01 Diffuse.jpg"} size={"175px"} alt={"wood_1"} is_draggable={false}/> -->
        </div>
    
    </div>

    <!-- <div class="tab-content" class:active={activeMaterialTab==='metal'} id="metal">
    
    </div> -->

</div>

<style>

    #material_library{
        text-align: center;
        align-items: center;
        /* justify-content: center; */
        overflow:auto;
        width:100%;
        height: 100%; 
        display:flex;
        flex-direction: column;
    }   

    #material_library.hidden{
        display:none;
    }

    .tabs{
        display:flex; 
        flex-direction: row;
    }

    .tab-btn {
        height:100%;
        border: black 1px solid;
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
        height: 50%;
        width:100%;
        padding: 5px;
        overflow: auto; 
        border: 1px solid black;
	}

    .image-grid {
        width:100%;
        margin:0 auto;
        display: grid;
        grid-template-columns: repeat(2, 1fr);
    }
</style>
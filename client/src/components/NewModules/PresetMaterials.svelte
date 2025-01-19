<script> 
    import {onMount} from 'svelte';
    import { Circle } from 'svelte-loading-spinners';
    import NumberSpinner from "svelte-number-spinner";
    import {design_brief} from '../../stores.js';
    import domtoimage from 'dom-to-image';

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
    let selected_texture = "";
    let selected_material_name="";
    let use_design_brief = true;

    let suggestions = [];
    let prompt = "";

    let toOutputGrid=false; 
    let n=4;
    let context=get(design_brief);

    let screenshotDiv; // reference to the div we want to capture


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
        context=get(design_brief);
    });

    async function similar_textures() {

    }

    function deselect(name) {
        if (selected_material_name===name) {
            selected_material_name="";
        } 
    }

    async function screenshot3DView() {
        const element = document.getElementById('3d-viewer');

        if(!element) {
            console.log("Element not found");
            alert("3D view not found");
            return;
        } 

        domtoimage.toPng(element).then((dataUrl) => {
            const link = document.createElement('a');
            link.href = dataUrl;
            link.download = 'screenshot.png';
            link.click();
        });


    }

    async function explore_materials() {
        toOutputGrid=false;
        suggestions=[];
        if (selected_material_name==="") {
            alert("Please select a material first");
            return;
        }
        selected_texture = preset_materials[selected_material_name];

        let material_response = await fetch("/get_materials", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                "prompt": prompt,
                "n": n,
                "design_brief": use_design_brief ? context : null,
                "image_path": selected_texture,
                "material_name": selected_material_name 
            }),
        });

        let materials_json = await material_response.json();
        let texture_prompts = materials_json["prompts"];
        let materials = materials_json["materials"];
        let explanations = materials_json["explanations"];

        console.log("Texture prompts: ", texture_prompts);

        // Generate n textures from the prompts
        for (let i=0; i<texture_prompts.length; i++) {
            let prompt = texture_prompts[i] + " texture map, seamless, 4k";

            let texture_response = await fetch("/generate_textures", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    "texture_string": prompt,
                    "n":1,
                    "imsize":448,
                }),
            });
            let results_json = await texture_response.json();
            let result = results_json["results"][0];
            let texture_map = result["texture"]
            suggestions.push({
                "material": materials[i],
                "texture_map": texture_map,
                "explanation": explanations[i]
            });
            suggestions=suggestions; 
        }
        
        console.log("Suggestions: ", suggestions);

    }

    async function explore_textures() {
        suggestions=[];
        if (selected_material_name==="") {
            alert("Please select a material first");
            return;
        }
        selected_texture = preset_materials[selected_material_name];
        // Get n material prompts from chatgpt
        toOutputGrid=true;
        

        let prompt_response = await fetch("/get_texture_prompts", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                "prompt": prompt,
                "n": n,
                "design_brief": use_design_brief ? context : null,
                "image_path": selected_texture,

            }),
        });


        let prompts_json = await prompt_response.json();
        let texture_prompts = prompts_json["texture_prompts"];
        console.log("Texture prompts: ", texture_prompts);

        // Generate n textures from the prompts
        for (let i=0; i<texture_prompts.length; i++) {
            let prompt = texture_prompts[i] + " texture map, seamless, 4k";

            let texture_response = await fetch("/generate_textures", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    "texture_string": prompt,
                    "n":1,
                    "imsize":448,
                }),
            });
            let results_json = await texture_response.json();
            let result = results_json["results"][0];
            let texture_map = result["texture"]
            suggestions.push({"texture_map": texture_map});
            suggestions=suggestions; 
        }
        
        console.log("Suggestions: ", suggestions);
    }

</script>

<div id="material_library">

    <div id="presets">
        <div class="image-grid">
            {#each Object.entries(preset_materials) as [name,path]}
                <label id="preset" class="column center" class:selected={selected_material_name===name}>
                    <!-- <input type=radio bind:group={selected_texture} name="option" value={path} > -->
                    <input type=radio bind:group={selected_material_name} name="option" value={name} 
                    on:click={() => {deselect(name);}} >
                    <strong> {name} </strong>
                    <DynamicImage imagepath={path} size={"200px"} alt={name} is_draggable={true}/>
                </label>
            {/each}
            <!-- <DynamicImage imagepath={"preset_materials/wood-01-1k/wood 01 Diffuse.jpg"} imagesource={"preset_materials/wood-01-1k/wood 01 Diffuse.jpg"} size={"175px"} alt={"wood_1"} is_draggable={false}/> -->
        </div>
    </div>
    <div id="input-area" class="column center">
        <textarea style="width:100%;height:100%;" bind:value="{prompt}" placeholder={"(Optional) Enter your prompt here.."} id="textarea"></textarea>
        <div class="row spaced center">
            <!-- <button style="width:25%;"> Similar Textures </button> -->
            <button style="width:25%;" on:click|preventDefault={()=>{
                explore_textures();
            }}> 
                Explore Textures 
            </button>
            <button style="width:25%;" on:click|preventDefault={()=>{
                explore_materials();
            }}> 
                Explore Materials 
            </button>
            <div class="column center">
                <label for="n"> Number of Outputs: </label>
                <NumberSpinner bind:value={n} min={1} max={10} step=1/>
            </div>
            <div class="column center">
                <label> Design brief </label>
                <input type="checkbox" bind:checked={use_design_brief} >
            </div>
        </div>
        
    </div>
    <div id="outputs" >
        <div class:image-grid={toOutputGrid} class:column={!toOutputGrid} class:center={!toOutputGrid}>
            {#each suggestions as suggestion}

                {#if toOutputGrid}
                    <DynamicImage imagepath={suggestion["texture_map"]} size={"200px"} alt={"suggestion"} is_draggable={true}/>
                {:else}
                    <div class="row spaced padded">
                        <div class="column centered">
                            <span> <strong> {suggestion["material"]}</strong>  </span>
                            <DynamicImage imagepath={suggestion["texture_map"]} size={"200px"} alt={"suggestion"} is_draggable={true}/>
                        </div>
                        <p> {suggestion["explanation"]} </p>
                    </div>
                {/if}

                
            {/each}
        </div>
    </div>
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

	#presets {
		display: flex;
        flex-direction: column;
        height: 40%;
        width:100%;
        padding: 5px;
        overflow: auto; 
        border: 1px solid black;
        margin-bottom: 5px;
	}

    #outputs {
        display: flex;
        flex-direction: column;
        height: 40%;
        width:100%;
        padding: 5px;
        overflow: auto; 
        border: 1px solid black;
        margin-bottom: 5px;
    }

    #input-area{
        width:100%;
        height:20%;
    }


    .image-grid {
        width:100%;
        margin:0 auto;
        display: grid;
        grid-template-columns: repeat(2, 1fr);
    }

    #preset input[type="radio"] {
        opacity: 0;
        position: fixed;
        width:0; 
    }

    #preset{
        margin:5px;
    }

    .selected{
        border: 3px solid blue;
    }

    .selected:hover{
        border: 3px solid blue;
    }

    #preset:hover{
        border: 3px solid grey;
    }


</style>
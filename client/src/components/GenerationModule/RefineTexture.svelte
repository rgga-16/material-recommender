<script>
    import { saved_color_palettes } from "../../stores.js";
    
    import DynamicImage from "../DynamicImage.svelte";
    import NumberSpinner from "svelte-number-spinner";
    import { Circle } from 'svelte-loading-spinners';
    import { onMount } from "svelte";
    import {actions_panel_tab} from "../../stores.js";

    export let selected_index; 
    export let rendering_texture_pairs;
    export let objs_and_parts; //Contains all the objects and parts in the scene including the ones that are not selected. Also indicates their rotation, scale, and location.
    export let selected_objs_and_parts_dict; //Contains the selected objects and parts in the scene. Does not indicate their rotation, scale, and location.

    
    let selected_obj=Object.keys(selected_objs_and_parts_dict)[0]; 
    let selected_part =selected_objs_and_parts_dict[selected_obj][0];


    function updateDisplayedColor() {
        let mat_color_div = document.getElementById("mat-color");
        mat_color_div.innerHTML='';

        let elements = [
            "<span> Material: " + rendering_texture_pairs[selected_index].info[selected_obj][selected_part]["mat_name"] + "</span>",
            "<div id='dynamic-image-container'></div>",
            "<span> Color: " + ("mat_color" in rendering_texture_pairs[selected_index].info[selected_obj][selected_part] ? rendering_texture_pairs[selected_index].info[selected_obj][selected_part]["mat_color"] : "None applied") + "</span>"
        ]
        let html = "";
        elements.forEach(element => {
            html += element;
        });
        mat_color_div.innerHTML = html;

        const dynamic_image_container = document.getElementById("dynamic-image-container");
        new DynamicImage({
            target: dynamic_image_container,
            props: {
                imagepath: rendering_texture_pairs[selected_index].info[selected_obj][selected_part]["mat_image_texture"],
                alt: selected_obj + " " + selected_part + " material",
                size: 175
            }
        });
    }
    
    
    function updateDisplayedMatFinish() {
        let mat_finish_div = document.getElementById("mat-finish");
        mat_finish_div.innerHTML='';
        mat_finish_div.innerHTML = "Current Material Finish: " + rendering_texture_pairs[selected_index].info[selected_obj][selected_part]["mat_finish"];
    }


    function updateDisplayedInfo() {
        updateDisplayedMatFinish();
        updateDisplayedColor();
    }

    function resetDisplayedInfo() {
        selected_part =selected_objs_and_parts_dict[selected_obj][0];
        updateDisplayedInfo();
    }


    let activeTab = "add-finish";
    function switchTab(tab) {
        activeTab = tab;
    }

    let x_loc = 0;
    let y_loc = 0;
    let z_rot = 0;
    let scale = 1.0;
    $: x_scale = scale;
    $: y_scale = scale;

    let material_finish;
    let material_finish_val=0.5;
    let psbdf_settings = {
        "Specular": 0.5,
        "Roughness": 0.5,
        "Clearcoat": 0.5,
        "Clearcoat Roughness": 0.5,
    }

    let palettes=[]; 
    let selected_palette_idx=0;
	saved_color_palettes.subscribe(value => {
		palettes=value;
        selected_palette_idx=0;
	});

    let isOpen=false;
    function toggleDropDown() {
        isOpen = !isOpen;
    }

    let selected_swatch_idx=undefined; 
    let no_color = {name: 'No Color', code: '#FFFFFF'}


    let dynamic_image;
    function updateRendering() {
        dynamic_image.getImage();
    }

    let is_loading;

    async function applyTransform() {
        is_loading=true; 
        const response = await fetch("/add_transform_to_rendering", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                "selected_obj": selected_obj,
                "selected_part": selected_part,
                "selected_textureparts": rendering_texture_pairs[selected_index].info,
                "selected_textureparts_path": rendering_texture_pairs[selected_index].info_path,
                "selected_rendering": rendering_texture_pairs[selected_index].rendering,
                "location":[x_loc,y_loc,0.0],
                "rotation":[0.0,0.0,z_rot],
                "scale":[x_scale,y_scale,1.0],
            }),
        });
        const json = await response.json();
        rendering_texture_pairs[selected_index].rendering = json["updated_rendering"]
        rendering_texture_pairs[selected_index].info = json["updated_textureparts"]
        rendering_texture_pairs[selected_index].info_path = json["updated_textureparts_path"]
        is_loading=false; 

        // Should return updated rendering and texture_parts json
        updateRendering();
        
    }

    async function applyFinish() {
        is_loading=true; 

        for (let setting in psbdf_settings) {
            if (setting=="Specular" || setting=="Clearcoat") {
                psbdf_settings[setting]=material_finish_val;
            } else if (setting=="Roughness" || setting=="Clearcoat Roughness") {
                psbdf_settings[setting]=1.0-material_finish_val;
            } else {
                psbdf_settings[setting]=0.5;
            }
        }

        // TEMPORARY CODE
        if(material_finish_val >= 0.5) {
            material_finish = "Glossy";
        } else {
            material_finish = "Matte";
        }
        
        const response = await fetch("/add_finish_to_rendering", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                "selected_obj": selected_obj,
                "selected_part": selected_part,
                "selected_textureparts": rendering_texture_pairs[selected_index].info,
                "selected_textureparts_path": rendering_texture_pairs[selected_index].info_path,
                "selected_rendering": rendering_texture_pairs[selected_index].rendering,
                "finish": material_finish,
                "psbdf_settings": psbdf_settings
            }),
        });
        const json = await response.json();
        rendering_texture_pairs[selected_index].rendering = json["updated_rendering"]
        rendering_texture_pairs[selected_index].info = json["updated_textureparts"]
        rendering_texture_pairs[selected_index].info_path = json["updated_textureparts_path"]
        is_loading=false; 

        console.log(rendering_texture_pairs[selected_index].info);

        updateDisplayedMatFinish();

        // Should return updated rendering and texture_parts json
        // updateRendering();

    }

    async function applyColor() {
        is_loading= true; 
        let code=undefined; 

        if (selected_swatch_idx!=undefined) { //Checks if a color has been selected.
            code = palettes[selected_palette_idx]['palette'][selected_swatch_idx];
        }

        const response = await fetch("/add_color_to_rendering", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                "selected_obj": selected_obj,
                "selected_part": selected_part,
                "selected_textureparts": rendering_texture_pairs[selected_index].info,
                "selected_textureparts_path": rendering_texture_pairs[selected_index].info_path,
                "selected_rendering": rendering_texture_pairs[selected_index].rendering,
                "color": code
            }),
        });
        const json = await response.json();
        rendering_texture_pairs[selected_index].rendering = json["updated_rendering"]
        rendering_texture_pairs[selected_index].info = json["updated_textureparts"]
        rendering_texture_pairs[selected_index].info_path = json["updated_textureparts_path"]

        is_loading = false; 
        // Should return updated rendering and texture_parts json
        // updateRendering();
        updateDisplayedColor();
    }

    function addDegree(val) {
        return val + "°";
    }

    function removeDegree(str) {
        return str.replace("°", "").trim();
    }


    function switchActionPanelTab(tab) {
        actions_panel_tab.set(tab);
    }

    onMount(async () => {
        resetDisplayedInfo();
    });


</script>

<h5> Refine material textures</h5> 
<select bind:value={selected_obj} on:change={()=> resetDisplayedInfo()}>
    <!-- {#each Object.keys(objs_and_parts) as obj} 
        <option value={obj}> {obj} </option> 
    {/each} -->
    {#each Object.keys(selected_objs_and_parts_dict) as obj} 
        <option value={obj}> {obj} </option> 
    {/each}
</select>

<div class="image">
    {#if is_loading}
        <Circle size="60" color="#FF3E00" unit="px" duration="1s" />
    {:else}
        <DynamicImage bind:this={dynamic_image} bind:imagepath={rendering_texture_pairs[selected_index].rendering} alt="rendering {selected_index}" size=500/>
    {/if}
</div>

<div class="w3-bar w3-grey tabs">
    <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='add-finish'} on:click={()=>switchTab('add-finish')} id="add-finish">Add Finish</button>
    <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='add-color'} on:click={()=>switchTab('add-color')} id="add-color">Add Color</button>
    <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='adjust-texture'} on:click={()=>switchTab('adjust-texture')} id="adjust-texture">Adjust Texture</button>
</div>

<div class='tab-content'  class:active={activeTab==='add-finish'} id="add-finish">
    <label>
        {selected_obj} part:
        <select bind:value={selected_part} on:change={()=> updateDisplayedMatFinish()}>
            {#each selected_objs_and_parts_dict[selected_obj] as part} 
                <option value={part}> {part} </option> 
            {/each}
            <!-- {#each objs_and_parts[selected_obj]['parts']['names'] as part} 
                <option value={part}> {part} </option> 
            {/each} -->
        </select>
    </label>

    <div id="mat-finish">
        <!-- This is where the material finish of the product part will be dynamically displayed -->
    </div>
<!-- 
    <label>
        Material finishes:
        <select bind:value={material_finish}>
            <option value={null}> None </option>
            <option value="glossy"> Glossy </option>
            <option value="matte"> Matte </option>
        </select>
    </label> -->

    <!-- {#if material_finish=='glossy' || material_finish=='matte'} -->
        <div class="control">
            <span>Matte</span>
            <NumberSpinner bind:value={material_finish_val} min=0.0 max=1.0 step=0.01 decimals=2 precision=0.01/>
            <span>Glossy</span>
        </div>
    <!-- {/if} -->

    <!-- 
        If Glossy, 
        - Increase Specular, Clearcoat,  (directly proportional)
        - Decrease Roughness, Clearcoat Roughness, (indirectly proportional)

        If Matte,
        - Increase Roughness, Clearcoat Roughness (indirectly proportional)
        - Decrease Specular, Clearcoat (directly proportional)

        Settings to adjust in the PSBDF:
            'Subsurface':0.0,
            'Specular':0.5,
            'Roughness':0.5,
            'Sheen Tint':0.5,
            'Clearcoat':0.0,
            'Clearcoat Roughness':0.95,
            'IOR':1.47,
    -->


    <button on:click|preventDefault={()=>applyFinish()}> Apply finish </button>

</div> 

<div class='tab-content' class:active={activeTab==='add-color'} id="add-color" >
    <label>
        {selected_obj} part:
        <select bind:value={selected_part} on:change={()=> updateDisplayedColor()}>
            {#each selected_objs_and_parts_dict[selected_obj] as part} <option value={part}> {part} </option> {/each}
            <!-- {#each objs_and_parts[selected_obj]['parts']['names'] as part} <option value={part}> {part} </option> {/each} -->
        </select> 
    </label>

    <div class="color-finish">
        <div class="color-selector">
            <div class="color-palette-header">
                
                <!-- No Colors Swatch Option -->
                <label class="swatch selectable" style="background-color: {no_color.code};" class:selected={selected_swatch_idx===undefined}>
                    <img src="./logos/cancel-svgrepo-com.svg" alt="">
                    <input type=radio bind:group={selected_swatch_idx} name={no_color.name} value={undefined}>
                </label>
                
                <!-- Color Swatch Options from the Selected Palette -->
                <div class="palette" style="position: relative;">
                    {#if selected_palette_idx != undefined && palettes.length > 0}
                        {#each palettes[selected_palette_idx]['palette'] as swatch, i }
                            <label class="swatch selectable" style="background-color: {swatch};" class:selected={selected_swatch_idx===i}>
                                <input type=radio bind:group={selected_swatch_idx} name={swatch} value={i}>
                            </label>
                        {/each}
                    {/if}

                    {#if isOpen}
                        <!-- Dropdown list of color palettes -->
                        <div class="dropdown-list" style="position: absolute; top: 30px; left: 0; z-index=1;" >
                            {#each palettes as p, j}
                                <label class="palette selectable" class:selected={selected_palette_idx===j}>
                                    {#each p["palette"] as swatch}
                                        <div class="swatch" style="background-color: {swatch};"></div>
                                    {/each}
                                    <input type=radio bind:group={selected_palette_idx} name={j} value={j}>
                                </label>
                            {/each}
                            <!-- svelte-ignore a11y-click-events-have-key-events -->
                            <div class="palette selectable" on:click={()=>switchActionPanelTab('suggest_colors')}> +Suggest colors </div>
                        </div>  
                    {/if} 
                </div>
                
                <!-- svelte-ignore a11y-click-events-have-key-events -->
                <div style=" width: 25px; height: 25px; align-items: center; justify-content: center; cursor: pointer;" on:click={toggleDropDown}> 
                    <img src="./logos/dropdown-svgrepo-com.svg" alt="Select a palette" style="width: 100%; height: 100%;" />
                </div>
                
            </div>
            {#if selected_swatch_idx===undefined}
                <div id="current-swatch">         
                    <pre>No color</pre> 
                </div>
            {:else }
                <input id="current-swatch" type="color"  bind:value={palettes[selected_palette_idx]['palette'][selected_swatch_idx]}>
            {/if}
            <button on:click|preventDefault={()=>applyColor()}> Apply to texture </button>

        </div>

        <div class="color-selector" id="mat-color">
            <!-- This is where the material color of the product part will be dynamically displayed -->
        </div>
    </div>
</div>

<div class='tab-content' class:active={activeTab==='adjust-texture'} id="adjust-texture">
    <label>
        {selected_obj} part:
        <select bind:value={selected_part}>
            {#each selected_objs_and_parts_dict[selected_obj] as part} 
                <option value={part}> {part} </option> 
            {/each}
        </select>
    </label>

    <div class="transforms">
        <div class="transform">
            Location
            <div class="control">
                <span>X:</span>
                <NumberSpinner bind:value={x_loc} min=0.0 max=10.0 step=0.1 decimals=1 precision=0.01/>
            </div>

            <div class="control">
                <span>Y:</span> 
                <NumberSpinner bind:value={y_loc} min=0.0 max=10.0 step=0.1 decimals=1 precision=0.01 />
            </div>
        </div>

        <div class="transform">
            Rotation
            <div class="control">
                <span>Z:</span>
                <NumberSpinner bind:value={z_rot} min=0 max=360 step=15 format={addDegree} parse={removeDegree}/>
            </div>
        </div>

        <div class="transform">
            Scale
            <div class="control">
                <span>X & Y:</span> 
                <NumberSpinner bind:value={scale} min=0.1 max=5.0 step=0.1 decimals=1 precision=0.01/>
            </div>

            <div class="control">
                <span>X:</span> 
                <NumberSpinner bind:value={x_scale} min=0.1 max=5.0 step=0.1 decimals=1 precision=0.01/>
            </div>
        
            <div class="control">
                <span>Y:</span> 
                <NumberSpinner bind:value={y_scale} min=0.1 max=5.0 step=0.1 decimals=1 precision=0.01/>
            </div>
        </div>
    </div>
    <button on:click|preventDefault={()=>applyTransform()} >Apply transforms</button>
</div>

<style>

    .image{
        object-fit: cover;
        width: 100%;
        max-width: 400px;
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

    .tab-content.active{
        border: 1px solid black;
    }

    .tab-content .color-finish{
        display:flex; 
        flex-direction: row;
        align-items: center;
        justify-content: space-between;
        border: 1px solid black;
    }

    .color-finish .color-selector {
        display:flex; 
        flex-direction: column;
        padding: 5px; 
        align-items: center;
        justify-content: center;
        border: 1px solid black; 
    }

    .color-selector .dropdown-list {
        background-color: #fff;
    }

    .color-selector .color-palette-header {
        display:flex; 
        flex-direction: row;
        align-items: center;
        justify-content: space-between;
        border: 1px solid black; 
        padding: 10px;
    }

    .palette {
        display:flex; 
        flex-direction: row;
        border: 1px solid black; 
        align-items: center; 
        justify-content: space-between;
        padding: 5px; 
    }

    .palette.selectable:hover {
        background-color: grey;
    }

    .palette.selectable.selected {
        background-color: rgb(86, 165, 255);
    }

    .palette.selectable.selected:hover {
        background-color: rgb(86, 165, 255);
    }

    .swatch {
        width: 25px; 
        height: 25px;
        border: 1px solid black; 
        margin-right: 2px;
    }

    #current-swatch {
        border: 1px solid black; 
        width: calc(6 * 25px + 2 * 2px);
        height: calc(6 * 25px + 2 * 2px);
        padding: 0;
    }

    input[type="color"]::-webkit-color-swatch-wrapper {
        padding: 0;
    }
    input[type="color"]::-webkit-color-swatch {
        border: none;
    }

    input[type="color"]:hover {
        cursor:pointer;
    }

    .selectable:hover {
        cursor:pointer;
    }

    .swatch.selectable:hover {
        border: 3px solid grey;
    }

    .swatch.selectable.selected {
        border: 3px solid blue;
    } 

    .swatch.selectable.selected:hover {
        border: 3px solid blue;
    } 

    input[type="radio"] {
        opacity: 0;
        position: fixed;
        width:0; 
    }

    .swatch * {
        width: 100%;
        height: 100%;
        align-items: center;
        justify-content: center;
    }

    .tab-content .transforms{
        display:flex; 
        flex-direction: row;
        align-items: center;
        justify-content: center;
        border: 1px solid black;
    }

    .tab-content .transforms .transform {
        border: 1px solid black;
        padding: 5px;
        margin: 5px;
        width: 100%;
        height: 100%;
    }

    .transform .control {
        display:flex; 
        align-items: center;
    }

  
	.tab-content.active {
		display: flex;
        flex-direction: column;
        padding: 5px;
	}

</style>
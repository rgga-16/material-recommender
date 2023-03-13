<script>
    import DynamicImage from "../DynamicImage.svelte";
    import NumberSpinner from "svelte-number-spinner";
    import { Circle } from 'svelte-loading-spinners';
    import { onMount } from "svelte";

    export let selected_index; 
    export let rendering_texture_pairs;
    export let objs_and_parts;
    export let selected_objs_and_parts_dict;

    console.log(objs_and_parts);

    let selected_obj=Object.keys(selected_objs_and_parts_dict)[0]; 
    let selected_part=selected_objs_and_parts_dict[selected_obj][0]; 

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

    let palettes = [
        [{name: 'Red', code: '#FF0000'},{name: 'Blue', code: '#0000FF'},{name: 'Green', code: '#008000'},{name: 'Yellow', code: '#FFFF00'},{name: 'Grey', code: '#D7D6D5'}],
        [{name: 'Blue', code: '#0000FF'},{name: 'Red', code: '#FF0000'},{name: 'Yellow', code: '#FFFF00'},{name: 'Green', code: '#008000'},{name: 'Grey', code: '#D7D6D5'}],
        [{name: 'Yellow', code: '#FFFF00'},{name: 'Grey', code: '#D7D6D5'},{name: 'Green', code: '#008000'},{name: 'Red', code: '#FF0000'},{name: 'Blue', code: '#0000FF'}]
    ];
    let selected_palette_idx=0;
    

    let isOpen=false;


    function toggleDropDown() {
        isOpen = !isOpen;
    }

    let selected_swatch_idx=0; 
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
        const response = await fetch("/add_finish_to_rendering", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                "selected_obj": selected_obj,
                "selected_part": selected_part,
                "selected_textureparts": rendering_texture_pairs[selected_index].info,
                "selected_textureparts_path": rendering_texture_pairs[selected_index].info_path,
                "selected_rendering": rendering_texture_pairs[selected_index].rendering,
                "finish": material_finish
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

    async function applyColor() {
        is_loading= true; 
        let code=undefined; 

        if (selected_swatch_idx!=undefined) { //Checks if a color has been selected. idx=0 is no color.
            code = palettes[selected_palette_idx][selected_swatch_idx].code;
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
        updateRendering();
    }

    function addDegree(val) {
        return val + "°";
    }

    function removeDegree(str) {
        return str.replace("°", "").trim();
    }

    onMount(() => {
        // addNoColorOption();


    });


</script>

<h5> Refine material textures</h5> 
<select bind:value={selected_obj}>
    {#each Object.keys(selected_objs_and_parts_dict) as obj} <option value={obj}> {obj} </option> {/each}
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
        <select bind:value={selected_part}>
            {#each selected_objs_and_parts_dict[selected_obj] as part} <option value={part}> {part} </option> {/each}
        </select>
    </label>
    Current Material Finish: {rendering_texture_pairs[selected_index].info[selected_obj][selected_part]["mat_finish"]}
    <label>
        Material finishes:
        <select bind:value={material_finish}>
            <option value={null}> None </option>
            <option value="glossy"> Glossy </option>
            <option value="matte"> Matte </option>
        </select>
    </label>
    <button on:click|preventDefault={()=>applyFinish()}> Apply finish </button>

</div> 

<div class='tab-content' class:active={activeTab==='add-color'} id="add-color" >
    <label>
        {selected_obj} part:
        <select bind:value={selected_part}>
            {#each selected_objs_and_parts_dict[selected_obj] as part} <option value={part}> {part} </option> {/each}
        </select>
    </label>

    <div class="color-finish">
        <div class="color-selector">
            <div class="color-palette-header">

                <label class="swatch" style="background-color: {no_color.code};" class:selected={selected_swatch_idx===undefined}>
                    <img src="./logos/cancel-svgrepo-com.svg" alt="">
                    <input type=radio bind:group={selected_swatch_idx} name={no_color.name} value={undefined}>
                </label>
                
                <div class="palette" style="position: relative;">
                    {#each palettes[selected_palette_idx] as swatch, i }
                        <label class="swatch selectable" style="background-color: {swatch.code};" class:selected={selected_swatch_idx===i}>
                            <input type=radio bind:group={selected_swatch_idx} name={swatch.name} value={i}>
                        </label>
                    {/each}
                    
                    {#if isOpen}
                        <div class="dropdown-list" style="position: absolute; top: 30px; left: 0; z-index=1;" >
                            {#each palettes as palette, j}
                                <label class="palette selectable" class:selected={selected_palette_idx===j}>
                                    {#each palette as swatch}
                                        <div class="swatch" style="background-color: {swatch.code};"></div>
                                    {/each}
                                    <input type=radio bind:group={selected_palette_idx} name={j} value={j}>
                                </label>
                            {/each}
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
                <input id="current-swatch" type="color"  bind:value={palettes[selected_palette_idx][selected_swatch_idx].code}>
            {/if}
            <button on:click|preventDefault={()=>applyColor()}> Apply to texture </button>

        </div>

        <div class="color-selector">
            <span> Material: {rendering_texture_pairs[selected_index].info[selected_obj][selected_part]["mat_name"]}</span>
            <DynamicImage bind:imagepath={rendering_texture_pairs[selected_index].info[selected_obj][selected_part]["mat_image_texture"]} alt="{selected_obj} {selected_part} material" size=175/>
            <span> Color: { "mat_color" in rendering_texture_pairs[selected_index].info[selected_obj][selected_part] ? rendering_texture_pairs[selected_index].info[selected_obj][selected_part]["mat_color"] : "None applied"} </span>
        </div>
    </div>
</div>

<div class='tab-content' class:active={activeTab==='adjust-texture'} id="adjust-texture">
    <label>
        {selected_obj} part:
        <select bind:value={selected_part}>
            {#each selected_objs_and_parts_dict[selected_obj] as part} <option value={part}> {part} </option> {/each}
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
        background-color: blue;
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

    .swatch.selectable:hover {
        border: 3px solid grey;
    }

    .swatch.selectable.selected {
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
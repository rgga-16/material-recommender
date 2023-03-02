<script>
    import DynamicImage from "../DynamicImage.svelte";
    export let selected_index; 
    export let rendering_texture_pairs;
    export let objs_and_parts;
    export let selected_objs_and_parts_dict;

    let selected_obj=Object.keys(selected_objs_and_parts_dict)[0]; 
    let selected_part=selected_objs_and_parts_dict[selected_obj][0]; 
    let material_finish;
    
    let activeTab = "tab1-content";
    function switchTab(tab) {
        activeTab = tab;
    }

    let x_loc = 0;
    let y_loc = 0;

    let z_rot = 0;

    let x_scale = 1.0;
    let y_scale = 1.0;

    let dynamic_image;
    function updateRendering() {
        dynamic_image.getImage();
    }

    async function applyTransformation() {

        const response = await fetch("/update_selected_rendering", {
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


        // Should return updated rendering and texture_parts json
        updateRendering();
    }

    async function applyFinish() {

    }


</script>

<h5> Refine material textures</h5> 
<select bind:value={selected_obj}>
    {#each Object.keys(selected_objs_and_parts_dict) as obj} <option value={obj}> {obj} </option> {/each}
</select>

<select bind:value={selected_part}>
    {#each selected_objs_and_parts_dict[selected_obj] as part} <option value={part}> {part} </option> {/each}
</select>

<div class="image">
    <DynamicImage bind:this={dynamic_image} bind:imagepath={rendering_texture_pairs[selected_index].rendering} alt="rendering {selected_index}" />
</div>

<div class="w3-bar w3-grey tabs">
    <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='tab1-content'} on:click={()=>switchTab('tab1-content')} id="tab1-btn">Texture Finish</button>
    <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='tab2-content'} on:click={()=>switchTab('tab2-content')} id="tab2-btn">Texture Orientation</button>
</div>

<div class='tab-content'  class:active={activeTab==='tab1-content'} id="add-finish">
    <label>
        {selected_obj} part:
        <select bind:value={selected_part}>
            {#each selected_objs_and_parts_dict[selected_obj] as part} <option value={part}> {part} </option> {/each}
        </select>
    </label>

    <label>
        Material finishes:
        <select bind:value={material_finish}>
            <option value="glossy"> Glossy </option>
            <option value="matte"> Matte </option>
        </select>

        <button on:click|preventDefault={applyFinish}> Apply finish </button>

        Current Material Finish: {rendering_texture_pairs[selected_index].info[selected_obj][selected_part]["mat_finish"]}
    </label>


    
</div> 

<div class='tab-content' class:active={activeTab==='tab2-content'} id="fix-orientation">
    <label>
        {selected_obj} part:
        <select bind:value={selected_part}>
            {#each selected_objs_and_parts_dict[selected_obj] as part} <option value={part}> {part} </option> {/each}
        </select>
    </label>

    <div class="transforms">
        <div class="transform">
            Location
            <label>
                x-axis
                <input type="range" min="-10.0" max="10.0" step="0.1" bind:value={x_loc} on:change|preventDefault={()=>applyTransformation()}/>
                <input type="number" min="-10.0" max="10.0" step="0.1" bind:value={x_loc} on:change|preventDefault={()=>applyTransformation()}/>
            </label>

            <label>
                y-axis
                <input type="range" min="-10.0" max="10.0" step="0.1" bind:value={y_loc} on:change|preventDefault={()=>applyTransformation()}/>
                <input type="number" min="-10.0" max="10.0" step="0.1" bind:value={y_loc} on:change|preventDefault={()=>applyTransformation()}/>
            </label>
        </div>

        <div class="transform">
            Rotation
            <label>
                z-axis 
                <input type="range" min="0" max="360" step="15" bind:value={z_rot} on:change|preventDefault={()=>applyTransformation()}/>
                <input type="number" min="0" max="360" step="1" bind:value={z_rot} on:change|preventDefault={()=>applyTransformation()}/>
            </label>
        </div>

        <div class="transform">
            Scale
            <label>
                x-axis
                <input type="range" min="0.0" max="5.0" step="0.1" bind:value={x_scale} on:change|preventDefault={()=>applyTransformation()}/>
                <input type="number" min="0.0" max="5.0" step="0.1" bind:value={x_scale} on:change|preventDefault={()=>applyTransformation()}/>
            </label>
        
            <label>
                y-axis
                <input type="range" min="0.0" max="5.0" step="0.1" bind:value={y_scale} on:change|preventDefault={()=>applyTransformation()}/>
                <input type="number" min="0.0" max="5.0" step="0.1" bind:value={y_scale} on:change|preventDefault={()=>applyTransformation()}/>
            </label>
        </div>

    </div>
    
    
    
</div>

<div class='tab-content' class:active={activeTab==='tab3-content'} id="add-color" >

    <!-- Rotate texture along z-axis -->


    <!-- Increasing size of texture -->
    
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

    .tab-content .transforms{
        display:flex; 
        flex-direction: row;
    }

    .tab-content .transforms .transform {
        border: 1px solid black;
    }
  
	.tab-content.active {
		display: flex;
        flex-direction: column;
        padding: 5px;
	}

</style>
<script>
    import DynamicImage from "../DynamicImage.svelte";
    export let selected_index; 
    export let rendering_texture_pairs;
    export let objs_and_parts;
    export let selected_objs_and_parts_dict;

    let selected_obj=Object.keys(selected_objs_and_parts_dict)[0]; 
    let selected_part=selected_objs_and_parts_dict[selected_obj][0]; 

    console.log(objs_and_parts);
    console.log(selected_objs_and_parts_dict);
    console.log(rendering_texture_pairs);
    
    let activeTab = "tab1-content";
    function switchTab(tab) {
        activeTab = tab;
    }

    let z_rot = 0;

    function handleRot() {

        console.log(z_rot);
    }


</script>

<h5> Refine material textures</h5> 
<select bind:value={selected_obj}>
    {#each Object.keys(selected_objs_and_parts_dict) as obj} <option value={obj}> {obj} </option> {/each}
</select>

<select bind:value={selected_part}>
    {#each selected_objs_and_parts_dict[selected_obj] as part} <option value={part}> {part} </option> {/each}
</select>

<DynamicImage imagepath={rendering_texture_pairs[selected_index].rendering} alt="rendering {selected_index}" />

<div class="w3-bar w3-grey tabs">
    <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='tab1-content'} on:click={()=>switchTab('tab1-content')} id="tab1-btn">Texture Finish</button>
    <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='tab2-content'} on:click={()=>switchTab('tab2-content')} id="tab2-btn">Texture Orientation</button>
</div>

<div class='tab-content'  class:active={activeTab==='tab1-content'} id="add-finish">
    
</div> 

<div class='tab-content' class:active={activeTab==='tab2-content'} id="fix-orientation">

    <!-- Rotate texture along z-axis -->
    <label>
        z-axis rotation 
        <input type="range" min="0" max="360" step="15" bind:value={z_rot} on:change|preventDefault={()=>handleRot()}/>
        <p> {z_rot} </p>
    </label>


    <!-- Increasing size of texture -->
    
</div>

<div class='tab-content' class:active={activeTab==='tab3-content'} id="add-color" >

    <!-- Rotate texture along z-axis -->


    <!-- Increasing size of texture -->
    
</div>


<style>

    img{
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
  
	.tab-content.active {
		display: flex;
        flex-direction: row;
        padding: 5px;
	}

</style>
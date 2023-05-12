<script>
	import { Circle } from 'svelte-loading-spinners';
	
	import ActionsPanel from "./components/ActionsPanel.svelte";
	import ThreeDDisplay from './components/ThreeDDisplay.svelte';
	import DynamicImage from "./components/DynamicImage.svelte";
	import Information from "./components/InformationPanel.svelte";
	import {curr_rendering_path} from './stores.js';
	import {curr_texture_parts} from './stores.js';
	import {curr_textureparts_path} from './stores.js';
	import {get} from 'svelte/store';
	import {onMount} from "svelte";	


	let current_rendering_path;
	let current_texture_parts;
	let current_textureparts_path;

	let saved_renderings = [];
	let selected_saved_rendering_idx; 
	let is_loading=false;

	let information_panel; 

	let current_rendering; 
	function updateCurrentRenderingDisplay() {
		current_rendering.getImage();
	}


	async function getSavedRenderings() {
		let response = await fetch('/get_saved_renderings');
		let data = await response.json();
		saved_renderings = await data["saved_renderings"]
		return data;
	}
	const saved_renderings_promise = getSavedRenderings();

	

	async function updateCurrentRendering() {
		is_loading=true;
		console.log("UPDATING CURRENT RENDERING");
		let response = await fetch('/get_current_rendering');
		const data = await response.json();

		curr_rendering_path.set(await data["rendering_path"]);
		curr_texture_parts.set(await data ["texture_parts"]);
		curr_textureparts_path.set(await data["textureparts_path"]);

		// updateCurrentRenderingDisplay();
		information_panel.updatePartInformation();
		is_loading=false;
	}
	

	let ui_collapsed = false;

	function collapseDiv(is_collapsed) {
		console.log("before: " + is_collapsed);
		if (is_collapsed===true) {
			is_collapsed=false;
		} else {
			is_collapsed=true;
		}
		console.log("after: " + is_collapsed);
	}

	async function saveRendering() {

		let curr_rendering_dict = {
			"rendering_path": current_rendering_path,
			"texture_parts": current_texture_parts,
			"textureparts_path": current_textureparts_path
		}

		const response = await fetch("/save_rendering", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(curr_rendering_dict),
        });
        const data = await response.json();
        saved_renderings = await data["saved_renderings"]
	}

	async function loadRendering(idx) {
		let selected = saved_renderings[idx];
		is_loading=true;

		const response = await fetch("/apply_to_current_rendering", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                "rendering_path": selected["rendering_path"],
                "texture_parts": selected["texture_parts"],
                "textureparts_path": selected["textureparts_path"]
            }),
        });

		// updateCurrentRendering();

        const data = await response.json();
		curr_rendering_path.set(await data["rendering_path"]);
		curr_texture_parts.set(await data["texture_parts"]);
		curr_textureparts_path.set(await data["textureparts_path"]);

		information_panel.updatePartInformation();

		is_loading=false;
		
	}

	curr_rendering_path.subscribe(value => {
		current_rendering_path = value;
	});

	curr_texture_parts.subscribe(value => {
		current_texture_parts = value;
	});

	curr_textureparts_path.subscribe(value => {
		current_textureparts_path = value;
	});

	async function getInitialRendering() {
		let response = await fetch('/get_current_rendering');
		let data = await response.json();
		curr_rendering_path.set(await data["rendering_path"]);
		curr_texture_parts.set(await data ["texture_parts"]);
		curr_textureparts_path.set(await data["textureparts_path"]);
		return data;
	}
	const promise = getInitialRendering();


	let activeDisplayTab='rendering_display';
	function switchDisplayTab(tab) {
        activeDisplayTab=tab;
    }



	onMount(async function () {
		const response = await fetch("/get_static_dir");
		const data = await response.text();	
	});


</script>

<main>

	<div class="container">
		<!-- Left Section -->
		<div class="actions-panel" class:collapsed={ui_collapsed}>
			<ActionsPanel onCallUpdateCurrentRendering={updateCurrentRendering}/> 
			<!-- <ActionsPanel/> -->
			<!-- <button on:click={()=>collapseDiv(ui_collapsed)}> Hide </button> -->
		</div>

		<!-- Middle Section  -->
		<div class="renderings">

			<div class="display-panel">
				<div class="w3-bar w3-grey tabs">
					<button class='w3-bar-item w3-button tab-btn' class:active={activeDisplayTab==='rendering_display'} on:click={()=>switchDisplayTab('rendering_display')} id="rendering-display-btn">Rendering View</button>
					<button class='w3-bar-item w3-button tab-btn' class:active={activeDisplayTab==='3d_display'} on:click={()=>switchDisplayTab('3d_display')} id="suggest-colors-btn">3D View</button>
				</div>

				<!-- Display rendering -->
				<div class="tab-content rendering-display" class:active={activeDisplayTab==='rendering_display'}>
					{#if is_loading}
						<div class="images-placeholder">
							<Circle size="60" color="#FF3E00" unit="px" duration="1s" />
						</div>
					{:else}
						{#await promise}
							<pre> Loading rendering. Please wait. </pre>
						{:then data} 
							<div class="image">
								<DynamicImage bind:this={current_rendering} imagepath={current_rendering_path} alt="Current rendering" size={"80%"}/>
								<button on:click|preventDefault={saveRendering}> Save rendering </button>
							</div>
							
						{/await}
					{/if}
				</div>

				<!-- Display 3D model/s -->
				<div class="tab-content threed-display" class:active={activeDisplayTab==='3d_display'}>
					<ThreeDDisplay />

				</div>
			</div>


			

			<!-- Display of saved renderings -->
			<div class="saved-renderings">
				{#await saved_renderings_promise}
					<pre> Loading saved renderings. Please wait. </pre>
				{:then data} 
					<form on:submit|preventDefault={loadRendering(selected_saved_rendering_idx)}>
						<h3>Saved Renderings</h3>
						<div class="saved-renderings-list"> 
							<button disabled={!(selected_saved_rendering_idx!=undefined)}> Load rendering </button>
							{#each saved_renderings as saved_renderings,i}
								<label class = "saved-rendering" class:selected={selected_saved_rendering_idx===i}>
									<input type=radio bind:group={selected_saved_rendering_idx} name="option-{i}" value={i} />
									<img src={saved_renderings["rendering_path"]} alt="saved rendering {i}" />
								</label>
							{/each}
						</div>
					</form>
				{/await}
			</div>
		</div>

		<div class="information-panel">
			{#await promise}
				<pre> Loading rendering information. Please wait. </pre>
			{:then data} 
				<Information bind:this={information_panel} />
			{/await}
			
		</div>

	</div>
</main>

<style>
	main{
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 99vh;
		width: 99vw;
	}
	.container {
		display: flex;
		flex-direction: row;
		height: 99%;
		width: 99%;
	}

	.actions-panel {
		width: 25%;
		background-color: lightgray;
		height: inherit;
		border: 2px solid black;
	}

	.information-panel {
		width: 25%; 
		background-color: lightgray;
		border: 2px solid black;
		height: inherit;
	}

	.renderings {
		width: 50%;
		height: inherit;
		padding: 5px;
	}

	.display-panel {
		justify-content: center;
		align-items: center;
		background-color: lightgray;
		border: 2px solid black;
		display:flex;
		flex-direction: column;
		padding:0px 0px 0px 0px;
		margin-bottom: 5px;
		height: 65%;
	}

	.rendering-display {
		justify-content: center;
		align-items: center;
		display:flex;
		flex-direction: column;
	}

	.rendering-display .image {
		display:flex;
		flex-direction: column;
		width:100%;
        height: 100%;
        object-fit: cover;
        /* border: solid 1px black;  */
		justify-content: center;
		align-items: center;
	}

	.images-placeholder {
        width: 100%;
        height: 100%;
        border: 1px dashed black;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
    }


	.rendering-display button{
		width: fit-content;
		position: relative; 
	}

	.saved-renderings{
		background-color: lightgray;
		border: 2px solid black;
		padding: 5px;
		height: 35%;
	}

	.saved-renderings-list{
		display: flex;
		overflow-x: auto;
		justify-content: left;
		padding:5px;
		scrollbar-width: none; /* Hide the scrollbar */
  		-ms-overflow-style: none; /* Hide the scrollbar on Edge */
	}
	
	.saved-rendering::-webkit-scrollbar {
		width:0;
		height:0;
	}
	.saved-renderings-list img{
		width:150px;
		height: 150px;
		margin:10px;
	}

	.saved-rendering {
		border: 1px solid grey;
	}

	.saved-rendering:hover {
		border: 3px solid grey;
	}

	.saved-rendering.selected {
		border: 3px solid blue;
	}

	.saved-rendering input[type="radio"] {
		opacity:0; 
		position:fixed; 
		width:0;
	}

	.user-interface button {
		position:relative;
		right:0;
		width:2rem;
		writing-mode: vertical-lr;
		text-orientation: upright;
	}

	.collapsed {
		display:none;
	}

	.tabs   {
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
        height: 100%;
        width:100%;
        padding: 5px;
	}
  </style>
  
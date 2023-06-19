<script>
	import { Circle } from 'svelte-loading-spinners';
	
	import ActionsPanel from "./components/ActionsPanel.svelte";
	import ThreeDDisplay from './components/ThreeDDisplay.svelte';
	import DynamicImage from "./components/DynamicImage.svelte";
	import Information from "./components/InformationPanel.svelte";
	import {curr_rendering_path} from './stores.js';
	import {curr_texture_parts} from './stores.js';
	import {curr_textureparts_path} from './stores.js';
	import {display_panel_tab} from './stores.js';
	import {displayWidth} from './stores.js';
	import {displayHeight} from './stores.js';
	import {objects_3d} from './stores.js';
	import {get} from 'svelte/store';
	import {onMount} from "svelte";	

	import * as THREE from 'three';
	import { GLTFExporter } from 'three/examples/jsm/exporters/GLTFExporter.js';
	import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
	import { saveAs } from 'file-saver';


	let current_rendering_path;
	let current_texture_parts;
	let current_textureparts_path;

	let saved_renderings = [];
	let selected_saved_rendering_idx; 


	let is_loading=false;
	let is_loading_rendering=false;
	let is_loading_saved_renderings = false;

	let information_panel; 
	let threed_display;

	let current_rendering; 
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
		// information_panel.updatePartInformation();
		is_loading=false;
	}
	

	let ui_collapsed = false;

	function collapseDiv(is_collapsed) {
		// console.log("before: " + is_collapsed);
		if (is_collapsed===true) {
			is_collapsed=false;
		} else {
			is_collapsed=true;
		}
		// console.log("after: " + is_collapsed);
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
		saved_renderings = [];
		selected_saved_rendering_idx=undefined;
		is_loading=true;
        saved_renderings = await data["saved_renderings"]
		is_loading=false;
	}

	async function loadRendering(idx) {
		let selected = saved_renderings[idx];
		console.log(selected);
		debugger;
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

        const data = await response.json();
		curr_rendering_path.set(await data["rendering_path"]);
		curr_texture_parts.set(await data["texture_parts"]);
		curr_textureparts_path.set(await data["textureparts_path"]);

		// information_panel.updatePartInformation();
		threed_display.update_3d_scene();

		is_loading=false;
		
	}

	curr_rendering_path.subscribe(value => {
		current_rendering_path = value;
	});

	curr_texture_parts.subscribe(value => {
		console.log(value);
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

	let activeDisplayTab='3d_display';

	display_panel_tab.subscribe(value => {
		activeDisplayTab = value;
	});

	function switchDisplayTab(tab) {
        display_panel_tab.set(tab);
    }

	async function render() {
		const renderpath = get(curr_rendering_path);
		const textureparts = get(curr_texture_parts);
		const texturepartspath = get(curr_textureparts_path);
		console.log(textureparts);

		const response = await fetch("/render", {
			method: "POST",
			headers: {"Content-Type": "application/json"},
			body: JSON.stringify({
				"renderpath": renderpath,
				"textureparts": textureparts,
				"texturepartspath": texturepartspath,
			}),
		});

		return "ok";
	}

	async function save_3d_models2() {
		// Needs 3D objects 
		let objects_3d_clone = get(objects_3d);
		console.log(objects_3d_clone);

		let current_texture_parts_ =get(curr_texture_parts);

		for (let i = 0; i < objects_3d_clone.length; i++) {
			let obj = objects_3d_clone[i];
			let obj_model = obj["model"];
			let obj_name = obj["name"];
			let obj_parent = obj["parent"];
			let url = obj["glb_url"]

			
			const response = await fetch("/save_model", {
				method: "POST",
				headers: {"Content-Type": "application/json"},
				body: JSON.stringify({
					"model": JSON.stringify(obj_model.toJSON(), null, 2),
					"texture_parts": current_texture_parts_,
					"name": obj_name,
					"parent": obj_parent,
					"url": url
				}),
			});

		}
		return "ok";
	}
	async function save_3d_models() {
		// Needs 3D objects 
		let objects_3d_clone = get(objects_3d);
		console.log(objects_3d_clone);

		let current_texture_parts_ =get(curr_texture_parts);

		for (let i = 0; i < objects_3d_clone.length; i++) {
			let exporter = new GLTFExporter();
			exporter.includeStandardMaterials = true;
			let obj = objects_3d_clone[i];
			let obj_model = obj["model"];
			let obj_name = obj["name"];
			let obj_parent = obj["parent"];
			let url = obj["glb_url"]

			exporter.parse(obj_model, 
			async function(result) {
				// console.log(obj_name + " " + obj_parent);
				// console.log(result);
				if(result instanceof ArrayBuffer) {
					console.log("is an array buffer");

				} else {
					// console.log("is not an array buffer");
					let output = JSON.stringify(result, null, 2);
					const response = await fetch("/save_model", {
						method: "POST",
						headers: {"Content-Type": "application/json"},
						body: JSON.stringify({
							"model": output,
							"texture_parts": current_texture_parts_,
							"name": obj_name,
							"parent": obj_parent,
							"url": url
						}),
					});
				}
			},
			function (error) {
				console.log("error for " + obj_name + ": " + error);
			});
		}
		return "ok";
	}


	async function update_3dmodels_and_render() {
		is_loading=true;
		const save_3d_resp = await save_3d_models();
		const render_resp = await render();
		is_loading=false;
		updateCurrentRendering();
		switchDisplayTab('rendering_display');
	}

	async function save_scene() {
		await update_3dmodels_and_render();
		saveRendering();
	}

	onMount(async function () {
		const response = await fetch("/get_static_dir");
		const data = await response.text();	
		const threediv = document.getElementById("display");
		displayWidth.set(threediv.offsetWidth);
		displayHeight.set(threediv.offsetHeight);
	});

</script>

<main>

	<div class="container">
		<!-- Left Section -->
		<div class="actions-panel" class:collapsed={ui_collapsed}>
			<ActionsPanel onCallUpdateCurrentRendering={updateCurrentRendering}/> 
			<!-- <button on:click={()=>collapseDiv(ui_collapsed)}> Hide </button> -->
		</div>

		<!-- Middle Section  -->
		<div class="renderings">
			<div class="display-panel" id="display">
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
								<button on:click|preventDefault={save_scene}>Save Scene</button>
								<!-- <button on:click|preventDefault={saveRendering}> Save rendering </button> -->
							</div>
						{/await}
					{/if}
				</div>


				<!-- Display 3D model/s -->
				<div class="tab-content threed-display" class:active={activeDisplayTab==='3d_display'} id="threed_display_parent">
						{#await promise}
							<pre> Loading 3D viewer. Please wait. </pre>
						{:then data}
							<ThreeDDisplay bind:this={threed_display} current_texture_parts={get(curr_texture_parts)} bind:information_panel={information_panel} {displayHeight} {displayWidth} />
							
							<div class="display-buttons">
								<button on:click|preventDefault={update_3dmodels_and_render}> Render </button>
								<button on:click|preventDefault={save_scene}>Save Scene</button>
							</div>
							
							{#if is_loading}
								<div class="images-placeholder" id="threed-loading">
									<Circle size="60" color="#FF3E00" unit="px" duration="1s" />
								</div>
							{/if}
						{/await}
					
				</div>

				
			</div>
			

			<!-- Display of saved renderings -->
			<div class="saved-renderings">
				{#await saved_renderings_promise}
					<pre> Loading saved renderings. Please wait. </pre>
				{:then data} 
					<form on:submit|preventDefault={loadRendering(selected_saved_rendering_idx)}>
						<h3>Saved Scenes</h3>
						<div class="saved-renderings-list"> 
							<button disabled={!(selected_saved_rendering_idx!=undefined)}> Load scene </button>
							{#if saved_renderings.length===0}
								{#if is_loading}
									<div class="images-placeholder">
										<Circle size="60" color="#FF3E00" unit="px" duration="1s" />
									</div>
								{:else}
									<div class="images-placeholder" style="height:100%;">
										No saved renderings yet.
									</div>
								{/if}
							{:else}
								{#each saved_renderings as saved_renderings,i}
									<label class = "saved-rendering" class:selected={selected_saved_rendering_idx===i}>
										<input type=radio bind:group={selected_saved_rendering_idx} name="option-{i}" value={i} />
										<img src={saved_renderings["rendering_path"]} alt="saved rendering {i}" />
									</label>
								{/each}
							{/if}
							
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
		width: 23%;
		background-color: lightgray;
		height: inherit;
		border: 2px solid black;
	}

	.information-panel {
		width: 27%; 
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

	.threed-display {
		position: relative;
		z-index: 1;
	}

	.display-buttons {
		display:flex;
		flex-direction: row;
		justify-content: center;
		align-items: center;
	}

	#threed-loading {
		position: absolute; /* set position to absolute */
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		z-index: 2; /* set z-index to a lower value than the container */
		background-color: rgba(255, 255, 255, 0.5); /* add a semi-transparent background */
		display: flex;
		justify-content: center;
		align-items: center;
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
		gap: 5px;
	}
  </style>
  
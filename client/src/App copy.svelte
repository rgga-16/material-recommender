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

		<!-- Middle Section  -->
		<div class="renderings">

			<div class="display-panel">
				<div class="w3-bar w3-grey tabs">
					<button class='w3-bar-item w3-button tab-btn' class:active={activeDisplayTab==='rendering_display'} on:click={()=>switchDisplayTab('rendering_display')} id="rendering-display-btn">Rendering View</button>
					<button class='w3-bar-item w3-button tab-btn' class:active={activeDisplayTab==='3d_display'} on:click={()=>switchDisplayTab('3d_display')} id="suggest-colors-btn">3D View</button>
				</div>

				<!-- Display 3D model/s -->
				<div class="tab-content threed-display" class:active={activeDisplayTab==='3d_display'}>
					<ThreeDDisplay />
				</div>
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

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
	import {threed_display_global} from './stores.js'
	import {information_panel_global} from './stores.js'
	import {objects_3d} from './stores.js';
	import {design_brief} from './stores.js';
	import {in_japanese} from './stores.js';
	import {use_chatgpt} from './stores.js';
	import {get} from 'svelte/store';
	import {onMount} from "svelte";	

	import {undoAction} from './main.js';
	import {redoAction} from './main.js';
	import {translate} from './main.js';

	import { GLTFExporter } from 'three/examples/jsm/exporters/GLTFExporter.js';

	let japanese;
    in_japanese.subscribe(value => {
        japanese = value;
    });


	let current_rendering_path;
	let current_texture_parts;
	let current_textureparts_path;

	let saved_renderings = [];
	let selected_saved_rendering_idx; 


	let is_loading=false;
	let is_loading_scene=false;
	let is_saving_scene = false; 
	let is_rendering_scene = false;
	let is_loading_saved_renderings = false;

	let information_panel; 
	information_panel_global.subscribe(value => {
		information_panel = value;
	});

	let threed_display;

	const saved_renderings_height = 35;
	const actions_panel_width = 23;
	const information_panel_width = 32;


	let curr_saved_renderings_height=saved_renderings_height;
	let curr_actions_panel_width = actions_panel_width;
	let curr_information_panel_width = information_panel_width;
	$: curr_display_panel_width = 100 - curr_actions_panel_width - curr_information_panel_width;
	$: curr_display_panel_height = 100 - curr_saved_renderings_height;

	let show_design_brief=false;
	function showDesignBrief() {
		show_design_brief=true;
	}

	let design_brief_textarea;
	function editDesignBrief() {
		design_brief_textarea.readOnly=false;
	}

	
	let design_brief_text="";
	async function translateDesignBrief(orig_design_brief_text) {
		const translated_design_brief = await translate("EN","JA",orig_design_brief_text);
		design_brief_text= await {...translated_design_brief};
	}

	// function updateDesignBrief() {
	// 	design_brief.set(design_brief_text);
	// 	design_brief_textarea.readOnly=true;
	// }

	function hideDesignBrief() {
		show_design_brief=false;
	}


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

	async function saveRendering() {
		is_saving_scene = true;
		is_loading_saved_renderings=true;
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
		
        saved_renderings = await data["saved_renderings"]
		is_loading_saved_renderings=false;
		is_saving_scene = false;
	}

	async function loadRendering(idx) {
		is_loading_scene=true;
		let selected = saved_renderings[idx];
		console.log(selected);
		
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
		is_loading_scene=false;
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
		is_rendering_scene=true;
		threed_display.removeHighlights();
		const save_3d_resp = await save_3d_models();
		const render_resp = await render();
		is_rendering_scene=false;
		updateCurrentRendering();
		switchDisplayTab('rendering_display');
	}

	async function save_scene() {
		// await update_3dmodels_and_render();
		saveRendering();
	}

	onMount(async function () {
		const response = await fetch("/get_static_dir");
		const data = await response.text();	
		const threediv = document.getElementById("display");
		displayWidth.set(threediv.offsetWidth);
		displayHeight.set(threediv.offsetHeight);
		threed_display_global.set(threed_display);
		information_panel_global.set(information_panel);
		console.log(get(curr_texture_parts));

		if (japanese) {
			await translateDesignBrief(get(design_brief));
		}
		else {
			design_brief_text={...get(design_brief)};
		}
	});

	let actions_panel_collapsed=false;
	function collapse_actions_panel() {
		if(actions_panel_collapsed===true) {
			curr_actions_panel_width = actions_panel_width; 
		} else {
			curr_actions_panel_width = 0.7;
		}
		actions_panel_collapsed = !actions_panel_collapsed;
	}
	
	let information_panel_collapsed=false;
	function collapse_information_panel() {
		if(information_panel_collapsed===true) {
			curr_information_panel_width = information_panel_width; 
		} else {
			curr_information_panel_width = 0.0;
		}
		information_panel_collapsed = !information_panel_collapsed;
	}

	let saved_renderings_collapsed=false; 
	function collapse_saved_renderings() {
		if(saved_renderings_collapsed===true) {
			curr_saved_renderings_height = saved_renderings_height; 
		} else {
			curr_saved_renderings_height = 0.0;
		}
		saved_renderings_collapsed = !saved_renderings_collapsed;
	}

</script>

<main>

	<div class="container">
		<!-- Left Section -->
		<div class="actions-panel" class:collapsed={actions_panel_collapsed} style="width: {curr_actions_panel_width}%;">
			
			<button class="collapse-button"on:click={() => collapse_actions_panel()} 
				style={actions_panel_collapsed ? "top: 90%; right: -185%; transform:rotate(270deg);" : "top: 90%; right: -10%; transform:rotate(270deg);"}
			>
				{#if actions_panel_collapsed}
					{japanese ? "展開する" : "Expand"}
					<img src="./logos/dropdown-svgrepo-com.svg" alt="" style="width: 20px; height: 20px;" />
				{:else}
					{japanese ? "折りたたむ": "Collapse"} 
					<img src="./logos/dropup-svgrepo-com.svg" alt="" style="width: 20px; height: 20px;" />
				{/if}
			</button>
			<ActionsPanel onCallUpdateCurrentRendering={updateCurrentRendering}/> 
		</div>

		<!-- Middle Section  -->
		<div class="renderings" style="width: {curr_display_panel_width}%;">
			<div class="display-panel" id="display" style="height: {curr_display_panel_height}%;">
				<button id="design-brief-btn" on:click = {() => showDesignBrief()}> {japanese ? "デザイン概要を見る" : "View Design Brief"} </button>
				
				<div id="action-history-btns">
					<button id="" on:click = {() => {undoAction()}}> 
						<img src="./logos/undo-small-svgrepo-com.svg" alt="" style="width: 20px; height: 20px;" />
					</button>
					<button id="" on:click = {() => {redoAction()}}> 
						<img src="./logos/redo-small-svgrepo-com.svg" alt="" style="width: 20px; height: 20px;" />
					</button>
				</div>
				
				
				<div class="w3-bar w3-grey tabs">
					<button class='w3-bar-item w3-button tab-btn' class:active={activeDisplayTab==='rendering_display'} on:click={()=>switchDisplayTab('rendering_display')} id="rendering-display-btn">Rendering View</button>
					<button class='w3-bar-item w3-button tab-btn' class:active={activeDisplayTab==='3d_display'} on:click={()=>switchDisplayTab('3d_display')} id="suggest-colors-btn">3D View</button>
					
				</div>
				<!-- Display rendering -->
				<div class="tab-content rendering-display" class:active={activeDisplayTab==='rendering_display'}>
					{#if is_loading_scene || is_rendering_scene || is_saving_scene}
						<div class="images-placeholder">
							{#if is_loading_scene}
								{japanese ? "ロード中...": "Loading scene..."}
							{:else if is_saving_scene}
								{japanese ? "保存シーン..." : "Saving scene..."}
							{:else if is_rendering_scene}
								{japanese ? "レンダリングシーン": "Rendering scene..."}
							{:else}
								{japanese ? "シーンの更新": "Updating scene..."}
							{/if}
							<Circle size="60" color="#FF3E00" unit="px" duration="1s" />
						</div>
					{:else}
						{#await promise}
							<pre> 
								{japanese ? "レンダリングを読み込んでいます。しばらくお待ちください。": "Loading rendering. Please wait."} 
							</pre>
						{:then data} 
							<div class="image">
								<DynamicImage bind:this={current_rendering} imagepath={current_rendering_path} alt="Current rendering" size={"80%"}/>
							</div>
							<div class="display-buttons"> 
								<button on:click|preventDefault={update_3dmodels_and_render}>
									{japanese ? "レンダー" : "Render"}  
								</button>
								<button on:click|preventDefault={save_scene}>
									{japanese ? "セーブシーン": "Save Scene"}
								</button>
							</div>

						{/await}
					{/if}
				</div>


				<!-- Display 3D model/s -->
				<div class="tab-content threed-display" class:active={activeDisplayTab==='3d_display'} id="threed_display_parent">
						{#await promise}
							<pre> 
								{japanese ? "3Dビューアをロードしています。しばらくお待ちください。": "Loading 3D viewer. Please wait."}
							</pre>
						{:then data}
							<ThreeDDisplay bind:this={threed_display} current_texture_parts={get(curr_texture_parts)} bind:information_panel={information_panel} {displayHeight} {displayWidth} />
							<div class="display-buttons">
								<button on:click|preventDefault={update_3dmodels_and_render}> {japanese ? "レンダー" : "Render"} </button>
								<button on:click|preventDefault={save_scene}>{japanese ? "セーブシーン": "Save Scene"}</button>
							</div>
							{#if is_loading_scene || is_rendering_scene || is_saving_scene}
								<div class="images-placeholder" id="threed-loading">
									{#if is_loading_scene}
										{japanese ? "ロード中...": "Loading scene..."}
									{:else if is_saving_scene}
										{japanese ? "保存シーン..." : "Saving scene..."}
									{:else if is_rendering_scene}
										{japanese ? "レンダリングシーン": "Rendering scene..."}
									{:else}
										{japanese ? "シーンの更新": "Updating scene..."}
									{/if}
									<Circle size="60" color="#FF3E00" unit="px" duration="1s" />
								</div>
							{/if}
						{/await}
				</div>
			</div>
			

			<!-- Display of saved renderings -->
			<div class="saved-renderings" style="height: {curr_saved_renderings_height}%;">
				<button class="collapse-button"on:click={() => collapse_saved_renderings()} style="top: 0%; right: 50%;">
					{#if saved_renderings_collapsed}
						{japanese ? "展開する" : "Expand"}
						<img src="./logos/dropup-svgrepo-com.svg" alt="" style="width: 20px; height: 20px;" />
					{:else}
						{japanese ? "折りたたむ": "Collapse"}
						<img src="./logos/dropdown-svgrepo-com.svg" alt="" style="width: 20px; height: 20px;" />
					{/if}
				</button>
				{#await saved_renderings_promise}
					<pre> Loading saved renderings. Please wait. </pre>
				{:then data} 
					<form on:submit|preventDefault={loadRendering(selected_saved_rendering_idx)}>
						<h3>
							{japanese ? "保存されたシーン": "Saved Scenes"}
						</h3>
						<div class="saved-renderings-list"> 
							<button disabled={!(selected_saved_rendering_idx!=undefined)}> Load scene </button>
							{#if saved_renderings.length===0}
								{#if is_loading_saved_renderings}
									<div class="images-placeholder">
										{japanese ? "保存されたシーンの更新...": "Updating saved scenes..."}
										<Circle size="60" color="#FF3E00" unit="px" duration="1s" />
									</div>
								{:else}
									<div class="images-placeholder" style="height:100%;">
										{japanese ? "保存されたレンダリングはまだない。": "No saved renderings yet."}
									</div>
								{/if}
							{:else}
								{#each saved_renderings as saved_renderings,i}
								
									<label class = "saved-rendering" class:selected={selected_saved_rendering_idx===i}>
										<input type=radio bind:group={selected_saved_rendering_idx} name="option-{i}" value={i} />
										<img src={saved_renderings["rendering_path"]} alt="saved rendering {i}" />
										<span> {japanese ? "シーン": "Scene"}  {i+1}</span>
									</label>
								{/each}
							{/if}
							
						</div>
					</form>
				{/await}
			</div>
		</div>

		<div class="information-panel" style="width: {curr_information_panel_width}%;">
			
			<button class="collapse-button"on:click={() => collapse_information_panel()} 
				style={information_panel_collapsed ? "top: 50%; left: -7%; transform:rotate(270deg);" : "top: 50%; left: -7%; transform:rotate(270deg);" }
			>
				{#if information_panel_collapsed}
					{japanese ? "展開する" : "Expand"}
					<img src="./logos/dropup-svgrepo-com.svg" alt="" style="width: 20px; height: 20px;" />
				{:else}
					{japanese ? "折りたたむ": "Collapse"}
					<img src="./logos/dropdown-svgrepo-com.svg" alt="" style="width: 20px; height: 20px;" />
				{/if}
			</button>
			{#await promise}
				<pre> Loading rendering information. Please wait. </pre>
			{:then data} 
				<Information bind:this={information_panel} />
			{/await}
			
		</div>

		<div id="design-brief-popup" class:show={show_design_brief} >
			<div id="design-brief-header" style="width:100%; height:auto; display:flex; flex-direction: row; background:lightgrey; justify-content:space-between;padding: 5px;">
				<h3>
					{japanese ? "デザイン・ブリーフ": "Design Brief"}
				</h3>
				<button  on:click|preventDefault={() => hideDesignBrief()}  >
					<img src="./logos/exit-svgrepo-com.svg" alt="" style="width: 30px; height: 30px;" />
				</button>	
				
			</div>
			<div id="design-brief-body" style="overflow:auto; flex-grow:1;">
				<textarea placeholder="No design brief yet. Please write your design brief here."
				readonly={true} bind:this={design_brief_textarea} 
				bind:value={design_brief_text} 
				style="width:100%; height:100%;"></textarea>
			</div>
			<div id="design-brief-footer" style="width:100%; height:auto; display:flex; flex-direction: row; background:lightgrey; align-content:center; justify-content:center;padding: 5px;">
				<!-- <button on:click|preventDefault={()=>editDesignBrief()}> Edit </button>
				<button on:click|preventDefault={() => {updateDesignBrief(); hideDesignBrief()}}> Save </button> -->
			</div>
		</div>
	</div>
</main>


<style>
	#design-brief-popup {
		display: none;
		position: absolute;
		z-index: 9999;
		top: 50%;
		left: 50%;
		width: 80%;
		height: 80%;
		transform: translate(-50%, -50%);
		overflow: auto;
		background: white; 
		border: 2px solid black;
		padding: 5px; 
	}

	#design-brief-popup.show {
		display: flex; 
		flex-direction: column;

	}


	main{
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 99vh;
		width: 99vw;
	}
	.container {
		position: relative;
		display: flex;
		flex-direction: row;
		height: 99%;
		width: 99%;
	}

	.collapse-button {
		position: absolute;
		
		z-index: 2;
	}

	.collapsed {
		overflow: hidden;
		transition: width 0.5 ease-out;
	}

	.actions-panel {
		position: relative;
		background-color: lightgray;
		height: inherit;
		border: 2px solid black;
	}

	.information-panel {
		position: relative;
		background-color: lightgray;
		border: 2px solid black;
		height: inherit;
	}

	.renderings {
		height: inherit;
		padding: 5px;
	}

	.display-panel {
		position: relative; 
		justify-content: center;
		align-items: center;
		background-color: lightgray;
		border: 2px solid black;
		display:flex;
		flex-direction: column;
		padding:0px 0px 0px 0px;
		margin-bottom: 5px;
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

	#design-brief-btn {
		position: absolute;
		z-index: 9999;
		top: 0;
		right: 0;
	}


	#action-history-btns {
		position: absolute;
		z-index: 9998;
		top: 0;
		right: 50;
		display:flex;
		flex-direction: row;
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
		position: relative;
		background-color: lightgray;
		border: 2px solid black;
		padding: 5px;
		
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
		display:flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		align-content:center;
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
  
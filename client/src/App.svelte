<script>
	import UserInterface from "./components/UserInterface.svelte";
	import RenderingDisplay from "./components/RenderingDisplay.svelte";
	import {curr_rendering_path} from './stores.js';
	import {curr_texture_parts} from './stores.js';
	import {curr_textureparts_path} from './stores.js';
	import {get} from 'svelte/store';

	let current_rendering_path;
	let current_texture_parts;
	let current_textureparts_path;

	let saved_renderings = [];
	let selected_saved_rendering_idx; 

	curr_rendering_path.subscribe(value => {
		current_rendering_path = get(curr_rendering_path);
	});

	curr_texture_parts.subscribe(value => {
		current_texture_parts = get(curr_texture_parts);
	});

	curr_textureparts_path.subscribe(value => {
		current_textureparts_path = get(curr_textureparts_path);
	});

	async function getSavedRenderings() {
		let response = await fetch('/get_saved_renderings');
		let data = await response.json();
		saved_renderings = await data["saved_renderings"]
		return data;
	}
	const saved_renderings_promise = getSavedRenderings();

	async function getInitialRendering() {
		let response = await fetch('/get_current_rendering');
		let data = await response.json();
		current_rendering_path = await data["rendering_path"];
		current_texture_parts = await data ["texture_parts"];
		current_textureparts_path = await data["textureparts_path"];
		return data; 
	}
	const promise = getInitialRendering();

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

		const response = await fetch("/apply_to_current_rendering", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                "rendering_path": selected["rendering_path"],
                "texture_parts": selected["texture_parts"],
                "textureparts_path": selected["textureparts_path"]
            }),
        });

        const json = await response.json();
        curr_rendering_path.set(json["rendering_path"]);
	}


</script>

<main>

	<div class="container">

		<div class="user-interface" class:collapsed={ui_collapsed}>
			<UserInterface />
			<!-- <button on:click={()=>collapseDiv(ui_collapsed)}> Hide </button> -->
		</div>

		<div class="renderings">
			<div class="rendering-display">
				{#await promise}
					<pre> Loading rendering. Please wait. </pre>
				{:then data} 
					<RenderingDisplay {current_rendering_path} />
					<button on:click|preventDefault={saveRendering}> Save rendering </button>
				{/await}
			</div>
			
			<div class="saved-renderings">
				{#await saved_renderings_promise}
					<pre> Loading saved renderings. Please wait. </pre>
				{:then data} 
					<h3>Saved Renderings</h3>
					<div class="saved-renderings-list">
						{#each saved_renderings as saved_renderings,i}
							<label class = "saved-rendering" class:selected={selected_saved_rendering_idx===i}>
								<input type=radio bind:group={selected_saved_rendering_idx} name="option-{i}" value={i} />
								<img src={saved_renderings["rendering_path"]} alt="saved rendering {i}" />
							</label>
						{/each}
					</div>
					<button style:opacity={selected_saved_rendering_idx!=undefined ? 1:0} on:click={() => loadRendering(selected_saved_rendering_idx)}> Load rendering </button>
				{/await}
			</div>
		</div>

		<div class="information-panel">
			<div class="w3-bar w3-grey tabs">
				<button class='w3-bar-item w3-button tab-btn' id="tab1-btn">Generate</button>
				<button class='w3-bar-item w3-button tab-btn'  id="tab2-btn">Suggest</button>
				<button class='w3-bar-item w3-button tab-btn'  id="tab3-btn">Feedback</button>
			</div>
		</div>
		

	</div>
</main>

<style>
	.container {
		display: flex;
		flex-direction: row;
		height: 100vh;
 		width: 100vw;
	}

	.user-interface {
		/* display:flex;
		flex-direction:row; */
	  	width: 20%;
	  	background-color: lightgray;
	}

	.renderings {
		width: 60%;
		padding: 0.5rem;
	}

	.information-panel {
		width: 20%; 
	}

	.rendering-display {
		justify-content: center;
	  	background-color: lightblue;
		border: 2px solid black;
		display:flex;
		flex-direction: column;
		padding:10px;
	}

	.rendering-display button{
		width: fit-content;
		position: relative; 
	}

	.saved-renderings{
		background-color: rgb(78, 230, 156) ;
		border: 2px solid black;
		padding:10px;
	}

	.saved-renderings-list{
		display: flex;
		overflow-x: scroll;
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
		width:175px;
		height: 175px;
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
  </style>
  
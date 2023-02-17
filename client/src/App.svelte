<script>
	import UserInterface from "./components/UserInterface.svelte";
	import RenderingDisplay from "./components/RenderingDisplay.svelte";
	import {curr_rendering_path} from './stores.js';
	import {get} from 'svelte/store';

	let current_rendering_path;
	let saved_renderings = [];

	curr_rendering_path.subscribe(value => {
		current_rendering_path = get(curr_rendering_path);
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
					<!-- <span> Rendering Path: {current_rendering_path}</span> -->
					<RenderingDisplay {current_rendering_path} />
				{/await}
			</div>
			
			<div class="saved-renderings">
				{#await saved_renderings_promise}
					<pre> Loading saved renderings. Please wait. </pre>
				{:then data} 
					<h3>Saved Renderings</h3>
					<div class="saved-renderings-list">
						{#each saved_renderings as saved_renderings,i}
							<img src={saved_renderings["rendering_path"]} alt="saved rendering {i}" />
						{/each}
					</div>
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
	  	
	  	background-color: lightblue;
		border: 2px solid black;
	}

	.saved-renderings{
		background-color: rgb(78, 230, 156) ;
		border: 2px solid black;
		/* padding:10px; */
	}

	.saved-renderings-list{
		display: flex;
		flex-wrap:wrap;
		justify-content: left;
		
	}
	.saved-renderings-list img{
		width:200px;
		height: 200px;
		margin:10px;
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
  
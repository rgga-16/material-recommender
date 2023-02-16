<script>
	import UserInterface from "./components/UserInterface.svelte";
	import RenderingDisplay from "./components/RenderingDisplay.svelte";
	import {curr_rendering_path} from './stores.js';
	import {get} from 'svelte/store';

	let current_rendering_path;

	curr_rendering_path.subscribe(value => {
		current_rendering_path = get(curr_rendering_path);
	});

	// I think you should call the initial rendering here.
	// https://codesource.io/how-to-fetch-json-in-svelte-example/

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
			<button on:click={()=>collapseDiv(ui_collapsed)}> Hide </button>
		</div>

		<div class="rendering-display">
			{#await promise}
				<pre> Loading rendering. Please wait. </pre>
			{:then data} 
				<h2>Current Rendering</h2>
				<!-- <span> Rendering Path: {current_rendering_path}</span> -->
				<RenderingDisplay {current_rendering_path} />
			{/await}
		</div>

	</div>
</main>

<style>
	.container {
		display: flex;
		flex-direction: row;
	}

	.user-interface button {
		position:relative;
		right:0;
		width:2rem;
		writing-mode: vertical-lr;
		text-orientation: upright;
	}

	.user-interface {
		display:flex;
		flex-direction:row;
	  	width: 25%;
	  	background-color: lightgray;
	}

	.user-interface.collapsed {
		display:none;
	}
	
	.rendering-display {
	  	width: 75%;
	  	background-color: lightblue;
	}
  </style>
  
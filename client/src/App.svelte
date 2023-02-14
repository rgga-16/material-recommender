<script>
	import {onMount} from "svelte";
	import UserInterface from "./components/UserInterface.svelte";
	import RenderingDisplay from "./components/RenderingDisplay.svelte";
	import {curr_rendering_path} from './stores.js';
	import {get} from 'svelte/store';

	let current_rendering_path;

	curr_rendering_path.subscribe(value => {
		current_rendering_path = get(curr_rendering_path);
	});

	const str = get(curr_rendering_path);

	// I think you should call the initial rendering here.
	// https://codesource.io/how-to-fetch-json-in-svelte-example/

	async function getInitialRendering() {
		let response = await fetch('/get_current_rendering');
		let data = await response.json();
		current_rendering_path = await data["rendering_path"];
		return data; 
	}

	const promise = getInitialRendering();

	// async function getChatGPTThing() {
	// 	const results_response = await fetch("https://chatgpt.pawan.krd/ask", {
    //         method: "POST",
    //         headers: {"Content-Type": "application/json"},
    //         body: JSON.stringify({
    //             "key": "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",
    //             "prompt": "who are you?",
    //             "id": "default"
    //         }), 
	// 	});

	// 	const results_json = await results_response.json();
	// 	console.log(results_json);
	// }

	// const thing = getChatGPTThing();


</script>

<main>

	<div class="container">
		<div class="user-interface">
			<UserInterface />
		</div>

		<div class="rendering-display">
			{#await promise}
				<pre> Loading rendering. Please wait. </pre>
			{:then data} 
				<h2>Current Rendering</h2>
				<span> Rendering Path: {current_rendering_path}</span>
				<RenderingDisplay {current_rendering_path} />
			{/await}
		</div>

	</div>
</main>

<style>
	.container {
		display: flex;
	}

	.user-interface {
	  	width: 30%;
	  	background-color: lightgray;
	}
	
	.rendering-display {
	  	width: 70%;
	  	background-color: lightblue;
	}
  </style>
  
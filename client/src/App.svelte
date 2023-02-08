<script>
	import UserInterface from "./components/UserInterface.svelte";
	import RenderingDisplay from "./components/RenderingDisplay.svelte";


	// I think you should call the initial rendering here.
	let data; 
	// https://codesource.io/how-to-fetch-json-in-svelte-example/
	onMount( async() => {
		const response = await fetch('/get_initial_rendering');
		data = await response.json();
		current_rendering_path = data["rendering_path"];
	});

</script>

<main>

	<div class="container">
		<div class="user-interface">
			<UserInterface />
		</div>

		<div class="rendering-display">
			<h2>Current Rendering {}</h2>
			<RenderingDisplay />
		</div>

	</div>
</main>

<style>
	.container {
		display: flex;
	  	/* height: 100vh; */
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
  
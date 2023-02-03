<script>
import UserInterface from "./components/UserInterface.svelte";

</script>

<main>

	<div class="container">
		<div class="user-interface">
			<UserInterface />
		</div>

		<div class="rendering-display">
			<h2>First Div</h2>
		</div>

	</div>
</main>

<style>
	.container {
		display: flex;
	  	height: 100vh;
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
  
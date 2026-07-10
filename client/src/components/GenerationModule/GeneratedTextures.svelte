<script>
	import DynamicImage from '../DynamicImage.svelte';

	let { pairs, selected_texture = $bindable(''), texture_name } = $props();

	function select(path) {
		selected_texture = path;
	}

	function handleKeydown(event, path) {
		if (event.key === 'Enter' || event.key === ' ') {
			event.preventDefault();
			select(path);
		}
	}
</script>

<div class="image-grid">
	{#each pairs as pair}
		<div
			class="texture-tile"
			class:selected={selected_texture === pair.texture}
			role="button"
			tabindex="0"
			onclick={() => select(pair.texture)}
			onkeydown={(event) => handleKeydown(event, pair.texture)}
		>
			<DynamicImage imagepath={pair.texture} size="100%" alt={texture_name} is_draggable={true} />
		</div>
	{/each}
</div>

<style>
	.image-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(96px, 1fr));
		gap: var(--sp-2);
		width: 100%;
	}

	.texture-tile {
		aspect-ratio: 1 / 1;
		overflow: hidden;
		background: var(--bg-elevated);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-lg);
		cursor: pointer;
		transition:
			border-color 120ms ease,
			transform 120ms ease;
	}

	.texture-tile:hover {
		border-color: var(--border-strong);
		transform: translateY(-1px);
	}

	.texture-tile.selected {
		border-color: var(--accent);
		box-shadow: 0 0 0 2px var(--accent);
	}
</style>

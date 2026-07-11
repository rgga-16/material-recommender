<script>
	import DynamicImage from '../DynamicImage.svelte';
	import Button from '../../lib/ui/Button.svelte';
	import RefreshCw from '@lucide/svelte/icons/refresh-cw';

	let { texture, rendering, size = '200px' } = $props();

	let currentImage = $state(0);
	let viewString = $derived(currentImage === 0 ? 'View texture' : 'View rendering');

	function switchImage() {
		currentImage = currentImage === 0 ? 1 : 0;
	}
</script>

<div class="preview-card">
	{#if rendering}
		<div class="image">
			{#if currentImage === 0}
				<DynamicImage imagepath={rendering} {size} alt="Rendering" />
			{:else}
				<DynamicImage imagepath={texture} {size} alt="Texture" />
			{/if}
		</div>
		<Button variant="secondary" size="sm" onclick={switchImage}>
			<RefreshCw size={14} strokeWidth={1.75} />
			{viewString}
		</Button>
	{:else}
		<div class="image">
			<DynamicImage imagepath={texture} {size} alt="Texture" />
		</div>
	{/if}
</div>

<style>
	.preview-card {
		display: flex;
		flex-direction: column;
		gap: var(--sp-2);
		background: var(--bg-elevated);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-lg);
		padding: var(--sp-2);
	}

	.image {
		width: 100%;
		border-radius: var(--radius-md);
		overflow: hidden;
	}
</style>

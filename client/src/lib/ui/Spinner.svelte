<script>
	let { size = 20 } = $props();
</script>

<span
	class="spinner"
	style:width="{size}px"
	style:height="{size}px"
	role="status"
	aria-label="Loading"
></span>

<style>
	.spinner {
		display: inline-block;
		border-radius: var(--radius-full);
		border: 2px solid rgba(255, 255, 255, 0.2);
		border-top-color: currentColor;
		color: var(--accent);
		animation: spin 0.7s linear infinite;
		flex-shrink: 0;
	}

	@media (prefers-reduced-motion: reduce) {
		.spinner {
			animation-duration: 1.4s;
		}
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}
</style>

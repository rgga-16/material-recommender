<script>
	let { title, padded = true, children, ...rest } = $props();
</script>

<div class="panel" {...rest}>
	{#if title}
		<div class="header">{title}</div>
	{/if}
	<div class="body" class:padded>
		{@render children?.()}
	</div>
</div>

<style>
	.panel {
		display: flex;
		flex-direction: column;
		height: 100%;
		background: var(--bg-panel);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-lg);
		overflow: hidden;
	}

	.header {
		flex-shrink: 0;
		padding: var(--sp-3);
		font-size: var(--text-sm);
		font-weight: 600;
		color: var(--text-primary);
		border-bottom: 1px solid var(--border-subtle);
	}

	.body {
		flex: 1;
		min-height: 0;
		overflow-y: auto;
	}

	.body.padded {
		padding: var(--sp-3);
	}
</style>

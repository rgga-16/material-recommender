<script>
	let { title, open = $bindable(true), children, actions } = $props();

	function toggle() {
		open = !open;
	}
</script>

<div class="section">
	<div class="header">
		<button type="button" class="toggle" onclick={toggle} aria-expanded={open}>
			<svg
				class="chevron"
				class:open
				viewBox="0 0 16 16"
				width="12"
				height="12"
				fill="none"
				stroke="currentColor"
				stroke-width="1.75"
			>
				<path d="M6 4l4 4-4 4" stroke-linecap="round" stroke-linejoin="round" />
			</svg>
			<span class="title">{title}</span>
		</button>
		{#if actions}
			<div class="actions">
				{@render actions()}
			</div>
		{/if}
	</div>
	{#if open}
		<div class="body">
			{@render children?.()}
		</div>
	{/if}
</div>

<style>
	.section {
		display: flex;
		flex-direction: column;
	}

	.header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		height: 32px;
		padding: 0 var(--sp-3);
		border-bottom: 1px solid var(--border-subtle);
	}

	.toggle {
		display: flex;
		align-items: center;
		gap: var(--sp-2);
		flex: 1;
		height: 100%;
		background: transparent;
		border: none;
		padding: 0;
		font-family: var(--font-sans);
		font-size: var(--text-sm);
		font-weight: 600;
		color: var(--text-secondary);
		text-align: left;
		cursor: pointer;
		transition: color 120ms ease;
	}

	.toggle:hover {
		color: var(--text-primary);
	}

	.chevron {
		flex-shrink: 0;
		transition: transform 120ms ease;
	}

	.chevron.open {
		transform: rotate(90deg);
	}

	.actions {
		display: flex;
		align-items: center;
		gap: var(--sp-2);
	}

	.body {
		padding: var(--sp-3);
	}
</style>

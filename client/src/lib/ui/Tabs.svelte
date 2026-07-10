<script>
	let { tabs = [], active, onSelect } = $props();
</script>

<div class="tabs" role="tablist">
	{#each tabs as tab (tab.id)}
		<button
			type="button"
			role="tab"
			class="tab"
			class:active={tab.id === active}
			aria-selected={tab.id === active}
			onclick={() => onSelect?.(tab.id)}
		>
			{#if tab.icon}
				<span class="icon">{@render tab.icon()}</span>
			{/if}
			{tab.label}
		</button>
	{/each}
</div>

<style>
	.tabs {
		display: flex;
		align-items: stretch;
		gap: var(--sp-4);
		height: 32px;
		border-bottom: 1px solid var(--border-subtle);
	}

	.tab {
		display: flex;
		align-items: center;
		gap: var(--sp-1);
		background: transparent;
		border: none;
		border-bottom: 2px solid transparent;
		margin-bottom: -1px;
		padding: 0;
		font-family: var(--font-sans);
		font-size: var(--text-sm);
		color: var(--text-secondary);
		cursor: pointer;
		transition:
			color 120ms ease,
			border-color 120ms ease;
	}

	.tab:hover {
		color: var(--text-primary);
	}

	.tab.active {
		color: var(--text-primary);
		border-bottom-color: var(--accent);
	}

	.icon {
		display: inline-flex;
	}
</style>

<script>
	let {
		image,
		label,
		selected = false,
		onclick,
		ondblclick,
		size = 96,
		aspect = '1/1',
		actions,
		children,
		...rest
	} = $props();

	function handleKeydown(e) {
		if (e.key === 'Enter' || e.key === ' ') {
			e.preventDefault();
			onclick?.(e);
		}
	}
</script>

<div
	class="card"
	class:selected
	role="button"
	tabindex="0"
	style:width="{size}px"
	{onclick}
	{ondblclick}
	onkeydown={handleKeydown}
	{...rest}
>
	<div class="thumb" style:aspect-ratio={aspect}>
		{#if image}
			<img src={image} alt={label ?? ''} />
		{:else}
			<div class="placeholder"></div>
		{/if}
		{#if actions}
			<div class="actions">
				{@render actions()}
			</div>
		{/if}
	</div>
	{#if label}
		<div class="label">{label}</div>
	{/if}
	{@render children?.()}
</div>

<style>
	.card {
		display: flex;
		flex-direction: column;
		background: var(--bg-elevated);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-lg);
		overflow: hidden;
		cursor: pointer;
		transition:
			border-color 120ms ease,
			transform 120ms ease;
	}

	.card:hover {
		border-color: var(--border-strong);
		transform: translateY(-1px);
	}

	.card.selected {
		border-color: var(--accent);
		box-shadow: 0 0 0 2px var(--accent);
	}

	.thumb {
		position: relative;
		width: 100%;
		background: var(--bg-inset);
		overflow: hidden;
	}

	.thumb img {
		display: block;
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.placeholder {
		width: 100%;
		height: 100%;
		background: var(--bg-inset);
	}

	.actions {
		position: absolute;
		left: 0;
		right: 0;
		bottom: 0;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: var(--sp-2);
		padding: var(--sp-2);
		background: rgba(0, 0, 0, 0.55);
		opacity: 0;
		visibility: hidden;
		transition:
			opacity 120ms ease,
			visibility 120ms ease;
	}

	.card:hover .actions,
	.card:focus-within .actions {
		opacity: 1;
		visibility: visible;
	}

	.label {
		padding: var(--sp-2) var(--sp-3);
		font-size: var(--text-sm);
		color: var(--text-secondary);
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}
</style>

<script>
	let {
		label,
		size = 'md',
		active = false,
		disabled = false,
		onclick,
		children,
		...rest
	} = $props();
</script>

<button
	type="button"
	class="icon-btn {size}"
	class:active
	aria-label={label}
	title={label}
	{disabled}
	{onclick}
	{...rest}
>
	{@render children?.()}
</button>

<style>
	.icon-btn {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 28px;
		height: 28px;
		padding: 0;
		border: none;
		border-radius: var(--radius-md);
		background: transparent;
		color: var(--text-secondary);
		cursor: pointer;
		transition:
			background 120ms ease,
			color 120ms ease;
	}

	.icon-btn.sm {
		width: 24px;
		height: 24px;
	}

	.icon-btn:hover:not(:disabled) {
		background: var(--bg-hover);
		color: var(--text-primary);
	}

	.icon-btn.active {
		background: var(--accent-muted);
		color: var(--accent);
	}

	.icon-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}
</style>

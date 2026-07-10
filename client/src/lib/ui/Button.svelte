<script>
	import Spinner from './Spinner.svelte';

	let {
		variant = 'secondary',
		size = 'md',
		disabled = false,
		loading = false,
		fullWidth = false,
		onclick,
		children,
		...rest
	} = $props();
</script>

<button
	type="button"
	class="btn {variant} {size}"
	class:full-width={fullWidth}
	disabled={disabled || loading}
	{onclick}
	{...rest}
>
	{#if loading}
		<Spinner size={14} />
	{/if}
	{@render children?.()}
</button>

<style>
	.btn {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		gap: var(--sp-2);
		height: 28px;
		padding: 0 var(--sp-3);
		border-radius: var(--radius-md);
		border: 1px solid transparent;
		background: transparent;
		font-family: var(--font-sans);
		font-size: var(--text-base);
		font-weight: 500;
		cursor: pointer;
		white-space: nowrap;
		transition:
			background 120ms ease,
			border-color 120ms ease,
			color 120ms ease;
	}

	.btn.sm {
		height: 24px;
		padding: 0 var(--sp-2);
		font-size: var(--text-sm);
	}

	.btn.full-width {
		width: 100%;
	}

	.btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	/* primary */
	.btn.primary {
		background: var(--accent);
		color: var(--text-on-accent);
	}
	.btn.primary:hover:not(:disabled) {
		background: var(--accent-hover);
	}

	/* secondary */
	.btn.secondary {
		background: var(--bg-elevated);
		border-color: var(--border-strong);
		color: var(--text-primary);
	}
	.btn.secondary:hover:not(:disabled) {
		background: var(--bg-hover);
	}

	/* ghost */
	.btn.ghost {
		background: transparent;
		color: var(--text-primary);
	}
	.btn.ghost:hover:not(:disabled) {
		background: var(--bg-hover);
	}

	/* danger */
	.btn.danger {
		background: transparent;
		border-color: var(--danger);
		color: var(--danger);
	}
	.btn.danger:hover:not(:disabled) {
		background: rgba(248, 113, 113, 0.12);
	}
</style>

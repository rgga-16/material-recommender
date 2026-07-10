<script>
	let { value = $bindable(''), placeholder = '', disabled = false, oninput, ...rest } = $props();

	function handleInput(e) {
		value = e.currentTarget.value;
		oninput?.(e);
	}
</script>

<textarea
	class="text-area"
	{placeholder}
	{disabled}
	{value}
	oninput={handleInput}
	{...rest}
></textarea>

<style>
	.text-area {
		display: block;
		width: 100%;
		min-height: 72px;
		padding: var(--sp-2) var(--sp-3);
		background: var(--bg-inset);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-md);
		font-family: var(--font-sans);
		font-size: var(--text-base);
		color: var(--text-primary);
		resize: vertical;
		transition:
			background 120ms ease,
			border-color 120ms ease,
			color 120ms ease;
	}

	.text-area::placeholder {
		color: var(--text-muted);
	}

	.text-area:hover:not(:disabled) {
		border-color: var(--border-strong);
	}

	.text-area:focus {
		border-color: var(--accent);
	}

	.text-area:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}
</style>

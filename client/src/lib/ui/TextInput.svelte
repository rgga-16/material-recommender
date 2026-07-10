<script>
	let {
		value = $bindable(''),
		placeholder = '',
		disabled = false,
		onEnter,
		oninput,
		...rest
	} = $props();

	function handleInput(e) {
		value = e.currentTarget.value;
		oninput?.(e);
	}

	function handleKeydown(e) {
		if (e.key === 'Enter') {
			onEnter?.(value);
		}
	}
</script>

<input
	type="text"
	class="text-input"
	{placeholder}
	{disabled}
	{value}
	oninput={handleInput}
	onkeydown={handleKeydown}
	{...rest}
/>

<style>
	.text-input {
		display: block;
		width: 100%;
		height: 28px;
		padding: 0 var(--sp-3);
		background: var(--bg-inset);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-md);
		font-family: var(--font-sans);
		font-size: var(--text-base);
		color: var(--text-primary);
		transition:
			background 120ms ease,
			border-color 120ms ease,
			color 120ms ease;
	}

	.text-input::placeholder {
		color: var(--text-muted);
	}

	.text-input:hover:not(:disabled) {
		border-color: var(--border-strong);
	}

	.text-input:focus {
		border-color: var(--accent);
	}

	.text-input:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}
</style>

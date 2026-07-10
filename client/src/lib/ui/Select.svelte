<script>
	let { value = $bindable(''), options = [], disabled = false, onchange, ...rest } = $props();

	function handleChange(e) {
		value = e.currentTarget.value;
		onchange?.(value);
	}
</script>

<select class="select" {disabled} {value} onchange={handleChange} {...rest}>
	{#each options as option (option.value)}
		<option value={option.value}>{option.label}</option>
	{/each}
</select>

<style>
	.select {
		display: block;
		width: 100%;
		height: 28px;
		padding: 0 var(--sp-5) 0 var(--sp-3);
		background-color: var(--bg-inset);
		background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6' viewBox='0 0 10 6' fill='none'%3E%3Cpath d='M1 1l4 4 4-4' stroke='%239aa3b2' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
		background-repeat: no-repeat;
		background-position: right var(--sp-3) center;
		appearance: none;
		-webkit-appearance: none;
		-moz-appearance: none;
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-md);
		font-family: var(--font-sans);
		font-size: var(--text-base);
		color: var(--text-primary);
		cursor: pointer;
		transition:
			background-color 120ms ease,
			border-color 120ms ease,
			color 120ms ease;
	}

	.select:hover:not(:disabled) {
		border-color: var(--border-strong);
	}

	.select:focus {
		border-color: var(--accent);
	}

	.select:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.select option {
		background: var(--bg-elevated);
		color: var(--text-primary);
	}
</style>

<script>
	let {
		value = $bindable(0),
		min,
		max,
		step = 1,
		decimals,
		unit,
		disabled = false,
		onInput = () => {},
		onCommit = () => {},
		...rest
	} = $props();

	function format(num) {
		if (decimals === undefined || decimals === null) return String(num);
		return Number(num).toFixed(decimals);
	}

	// Writable derived: tracks the bound value, but the user's in-progress
	// keystrokes overwrite it until the next external value change.
	let displayValue = $derived(format(value));

	function clamp(num) {
		let result = num;
		if (min !== undefined && min !== null) result = Math.max(Number(min), result);
		if (max !== undefined && max !== null) result = Math.min(Number(max), result);
		return result;
	}

	// One onCommit per edit: consumers push an undo/redo history entry per
	// commit, so a blur without any edit must not fire one.
	let dirty = false;

	function handleInput(event) {
		displayValue = event.currentTarget.value;
		const parsed = parseFloat(displayValue);
		if (!Number.isNaN(parsed)) {
			value = parsed;
			dirty = true;
			onInput(parsed);
		}
	}

	function commit() {
		if (!dirty) return;
		dirty = false;
		const parsed = parseFloat(displayValue);
		const clamped = clamp(Number.isNaN(parsed) ? value : parsed);
		value = clamped;
		displayValue = format(clamped);
		onCommit(clamped);
	}

	function handleBlur() {
		commit();
	}

	function handleKeydown(event) {
		if (event.key === 'Enter') {
			event.currentTarget.blur();
			return;
		}
		if (event.key === 'ArrowUp' || event.key === 'ArrowDown') {
			event.preventDefault();
			const delta = event.key === 'ArrowUp' ? Number(step) : -Number(step);
			const next = clamp((Number.isNaN(parseFloat(displayValue)) ? Number(value) : parseFloat(displayValue)) + delta);
			value = next;
			displayValue = format(next);
			dirty = true;
			onInput(next);
		}
	}
</script>

<div class="number-input" class:disabled>
	<input
		type="text"
		inputmode="decimal"
		class="field"
		{disabled}
		value={displayValue}
		oninput={handleInput}
		onblur={handleBlur}
		onkeydown={handleKeydown}
		{...rest}
	/>
	{#if unit}
		<span class="unit">{unit}</span>
	{/if}
</div>

<style>
	.number-input {
		display: inline-flex;
		align-items: center;
		gap: var(--sp-1);
		width: 72px;
		height: 28px;
		padding: 0 var(--sp-3);
		background: var(--bg-inset);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-md);
		transition:
			border-color 120ms ease,
			background 120ms ease;
	}

	.number-input:hover {
		border-color: var(--border-strong);
	}

	.number-input:focus-within {
		border-color: var(--accent);
	}

	.number-input.disabled {
		opacity: 0.5;
	}

	.field {
		flex: 1;
		width: 100%;
		min-width: 0;
		background: transparent;
		border: none;
		outline: none;
		color: var(--text-primary);
		font-size: var(--text-base);
		text-align: left;
	}

	.field::-webkit-outer-spin-button,
	.field::-webkit-inner-spin-button {
		-webkit-appearance: none;
		margin: 0;
	}

	.unit {
		flex-shrink: 0;
		color: var(--text-muted);
		font-size: var(--text-xs);
	}
</style>

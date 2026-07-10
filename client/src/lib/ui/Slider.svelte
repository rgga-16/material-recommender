<script>
	let {
		value = $bindable(0),
		min = 0,
		max = 100,
		step = 1,
		disabled = false,
		onInput = () => {},
		onCommit = () => {},
		showValue = true,
		...rest
	} = $props();

	let percent = $derived(
		max > min ? ((Number(value) - Number(min)) / (Number(max) - Number(min))) * 100 : 0
	);
	let trackBackground = $derived(
		`linear-gradient(to right, var(--accent) ${percent}%, var(--border-strong) ${percent}%)`
	);

	// One onCommit per user gesture: consumers push an undo/redo history entry
	// per commit, so duplicate/no-op commits corrupt history. A commit only
	// fires if an input happened since the previous commit.
	let dirty = false;

	function handleInput(event) {
		value = Number(event.currentTarget.value);
		dirty = true;
		onInput(value);
	}

	function handleCommit(event) {
		if (!dirty) return;
		dirty = false;
		value = Number(event.currentTarget.value);
		onCommit(value);
	}
</script>

<div class="slider" class:disabled>
	<input
		type="range"
		class="track"
		{min}
		{max}
		{step}
		{disabled}
		{value}
		style:background={trackBackground}
		oninput={handleInput}
		onchange={handleCommit}
		{...rest}
	/>
	{#if showValue}
		<span class="value">{value}</span>
	{/if}
</div>

<style>
	.slider {
		display: flex;
		align-items: center;
		gap: var(--sp-2);
		width: 100%;
	}

	.track {
		-webkit-appearance: none;
		appearance: none;
		flex: 1;
		height: 4px;
		border-radius: var(--radius-full);
		outline: none;
		cursor: pointer;
		transition:
			background 120ms ease,
			border-color 120ms ease,
			color 120ms ease;
	}

	.track::-webkit-slider-thumb {
		-webkit-appearance: none;
		appearance: none;
		width: 12px;
		height: 12px;
		border-radius: var(--radius-full);
		background: var(--text-primary);
		border: 2px solid var(--accent);
		cursor: pointer;
		transition:
			background 120ms ease,
			border-color 120ms ease;
	}

	.track::-moz-range-thumb {
		width: 12px;
		height: 12px;
		border-radius: var(--radius-full);
		background: var(--text-primary);
		border: 2px solid var(--accent);
		cursor: pointer;
		transition:
			background 120ms ease,
			border-color 120ms ease;
	}

	.track::-moz-range-track {
		height: 4px;
		border-radius: var(--radius-full);
		background: transparent;
	}

	.slider.disabled .track {
		cursor: not-allowed;
		opacity: 0.5;
	}

	.value {
		min-width: 2.5em;
		text-align: right;
		font-size: var(--text-xs);
		color: var(--text-secondary);
		flex-shrink: 0;
	}
</style>

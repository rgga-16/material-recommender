<script>
	let { checked = $bindable(false), disabled = false, onchange = () => {}, label, ...rest } = $props();

	function toggle(event) {
		checked = event.currentTarget.checked;
		onchange(checked);
	}
</script>

<label class="switch" class:disabled>
	<input type="checkbox" role="switch" {checked} {disabled} onchange={toggle} {...rest} />
	<span class="track">
		<span class="knob"></span>
	</span>
	{#if label}
		<span class="label">{label}</span>
	{/if}
</label>

<style>
	.switch {
		display: inline-flex;
		align-items: center;
		gap: var(--sp-2);
		cursor: pointer;
		width: fit-content;
	}

	.switch.disabled {
		cursor: not-allowed;
		opacity: 0.5;
	}

	.switch input {
		position: absolute;
		width: 1px;
		height: 1px;
		padding: 0;
		margin: -1px;
		overflow: hidden;
		clip: rect(0, 0, 0, 0);
		white-space: nowrap;
		border: 0;
	}

	.track {
		position: relative;
		display: inline-block;
		width: 32px;
		height: 18px;
		flex-shrink: 0;
		background: var(--bg-active);
		border-radius: var(--radius-full);
		transition: background 120ms ease;
	}

	.switch input:checked + .track {
		background: var(--accent);
	}

	.switch input:focus-visible + .track {
		outline: none;
		box-shadow: var(--ring);
	}

	.knob {
		position: absolute;
		top: 2px;
		left: 2px;
		width: 14px;
		height: 14px;
		border-radius: var(--radius-full);
		background: var(--text-primary);
		transition: transform 120ms ease;
	}

	.switch input:checked + .track .knob {
		transform: translateX(14px);
	}

	.label {
		font-size: var(--text-base);
		color: var(--text-primary);
		white-space: nowrap;
	}
</style>

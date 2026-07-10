<script>
	let { label, hint, row = false, children, ...rest } = $props();
</script>

<div class="field" class:row {...rest}>
	{#if label}
		<label class="field-label">{label}</label>
	{/if}
	<div class="field-control">
		{@render children?.()}
		{#if hint}
			<div class="field-hint">{hint}</div>
		{/if}
	</div>
</div>

<style>
	.field {
		display: flex;
		flex-direction: column;
	}

	.field.row {
		flex-direction: row;
		align-items: center;
	}

	.field-label {
		font-size: var(--text-xs);
		color: var(--text-secondary);
		font-weight: 500;
		margin-bottom: var(--sp-1);
	}

	.field.row .field-label {
		flex: 0 0 96px;
		margin-bottom: 0;
	}

	.field-control {
		flex: 1;
		min-width: 0;
	}

	.field-hint {
		font-size: var(--text-xs);
		color: var(--text-muted);
		margin-top: var(--sp-1);
	}
</style>

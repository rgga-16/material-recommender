<script>
	let { text, position = 'top', children, ...rest } = $props();
</script>

<span class="tooltip-wrap" {...rest}>
	{@render children?.()}
	<span class="tooltip-bubble {position}" role="tooltip">{text}</span>
</span>

<style>
	.tooltip-wrap {
		position: relative;
		display: inline-flex;
	}

	.tooltip-bubble {
		position: absolute;
		z-index: 100;
		padding: var(--sp-1) var(--sp-2);
		border-radius: var(--radius-sm);
		background: var(--bg-elevated);
		box-shadow: var(--shadow-overlay);
		color: var(--text-primary);
		font-size: var(--text-xs);
		white-space: nowrap;
		pointer-events: none;
		opacity: 0;
		visibility: hidden;
		transition:
			opacity 120ms ease,
			visibility 120ms ease;
		transition-delay: 0s;
	}

	.tooltip-wrap:hover .tooltip-bubble,
	.tooltip-wrap:focus-within .tooltip-bubble {
		opacity: 1;
		visibility: visible;
		transition-delay: 300ms;
	}

	.tooltip-bubble.top {
		bottom: calc(100% + var(--sp-1));
		left: 50%;
		transform: translateX(-50%);
	}

	.tooltip-bubble.bottom {
		top: calc(100% + var(--sp-1));
		left: 50%;
		transform: translateX(-50%);
	}

	.tooltip-bubble.left {
		right: calc(100% + var(--sp-1));
		top: 50%;
		transform: translateY(-50%);
	}

	.tooltip-bubble.right {
		left: calc(100% + var(--sp-1));
		top: 50%;
		transform: translateY(-50%);
	}
</style>

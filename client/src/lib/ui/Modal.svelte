<script>
	import X from '@lucide/svelte/icons/x';
	import IconButton from './IconButton.svelte';

	let {
		open = $bindable(false),
		title,
		width = '560px',
		onClose,
		children,
		footer,
		...rest
	} = $props();

	function close() {
		onClose?.();
	}

	function onKeydown(e) {
		if (e.key === 'Escape') {
			close();
		}
	}

	function onBackdropClick(e) {
		if (e.target === e.currentTarget) {
			close();
		}
	}
</script>

<svelte:window onkeydown={open ? onKeydown : undefined} />

{#if open}
	<div class="backdrop" onclick={onBackdropClick}>
		<div
			class="modal"
			style:width
			role="dialog"
			aria-modal="true"
			aria-label={title}
			{...rest}
		>
			<div class="header">
				<span class="title">{title}</span>
				<IconButton label="Close" onclick={close}>
					<X size={16} strokeWidth={1.75} />
				</IconButton>
			</div>
			<div class="body">
				{@render children?.()}
			</div>
			{#if footer}
				<div class="footer">
					{@render footer()}
				</div>
			{/if}
		</div>
	</div>
{/if}

<style>
	.backdrop {
		position: fixed;
		inset: 0;
		z-index: 1000;
		display: flex;
		align-items: center;
		justify-content: center;
		background: rgba(0, 0, 0, 0.55);
		backdrop-filter: blur(2px);
	}

	.modal {
		display: flex;
		flex-direction: column;
		max-width: calc(100vw - var(--sp-6));
		background: var(--bg-elevated);
		border-radius: var(--radius-lg);
		box-shadow: var(--shadow-modal);
	}

	.header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		flex: none;
		height: 48px;
		padding: 0 var(--sp-2) 0 var(--sp-4);
		border-bottom: 1px solid var(--border-subtle);
	}

	.title {
		font-size: var(--text-md);
		font-weight: 600;
		color: var(--text-primary);
	}

	.body {
		flex: 1 1 auto;
		max-height: 70vh;
		overflow-y: auto;
		padding: var(--sp-4);
	}

	.footer {
		display: flex;
		align-items: center;
		justify-content: flex-end;
		gap: var(--sp-2);
		flex: none;
		padding: var(--sp-3) var(--sp-4);
		border-top: 1px solid var(--border-subtle);
	}
</style>

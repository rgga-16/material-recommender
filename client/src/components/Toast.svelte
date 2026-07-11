<script>
    import { fade } from 'svelte/transition';
    import { toasts } from '../stores.js';

    let current_toasts = $derived($toasts);

    function dismiss(toast) {
        toast.onClick?.();
        toasts.update(current => current.filter(t => t.id !== toast.id));
    }
</script>

<div class="toast-stack" aria-live="polite">
    {#each current_toasts as toast (toast.id)}
        <button
            type="button"
            class="toast toast-{toast.type}"
            transition:fade={{ duration: 200 }}
            onclick={() => dismiss(toast)}
        >
            {toast.message}
        </button>
    {/each}
</div>

<style>
    .toast-stack {
        position: fixed;
        top: var(--sp-3);
        right: var(--sp-3);
        z-index: 9999;
        display: flex;
        flex-direction: column;
        gap: var(--sp-2);
        max-width: 320px;
        pointer-events: none;
    }

    .toast {
        pointer-events: auto;
        cursor: pointer;
        text-align: left;
        font-family: var(--font-sans);
        font-size: var(--text-sm);
        color: var(--text-primary);
        background: var(--bg-elevated);
        padding: var(--sp-2) var(--sp-3);
        border: none;
        border-left: 3px solid var(--accent);
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-overlay);
        animation: toast-in 180ms ease-out;
    }

    .toast-info {
        border-left-color: var(--accent);
    }

    .toast-success {
        border-left-color: var(--success);
    }

    .toast-error {
        border-left-color: var(--danger);
    }

    @keyframes toast-in {
        from {
            opacity: 0;
            transform: translateX(12px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
</style>

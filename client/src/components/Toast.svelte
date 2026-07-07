<script>
    import { fade } from 'svelte/transition';
    import { toasts } from '../stores.js';

    let current_toasts = [];
    toasts.subscribe(value => {
        current_toasts = value;
    });

    function dismiss(id) {
        toasts.update(current => current.filter(t => t.id !== id));
    }
</script>

<div class="toast-stack" aria-live="polite">
    {#each current_toasts as toast (toast.id)}
        <button
            type="button"
            class="toast toast-{toast.type}"
            transition:fade={{ duration: 200 }}
            on:click={() => dismiss(toast.id)}
        >
            {toast.message}
        </button>
    {/each}
</div>

<style>
    .toast-stack {
        position: fixed;
        top: 12px;
        right: 12px;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        gap: 8px;
        max-width: 320px;
        pointer-events: none;
    }

    .toast {
        pointer-events: auto;
        cursor: pointer;
        text-align: left;
        font-family: inherit;
        font-size: 0.95em;
        color: white;
        padding: 10px 14px;
        border: none;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }

    .toast-info {
        background-color: #2c6e8f;
    }

    .toast-success {
        background-color: #2e7d32;
    }

    .toast-error {
        background-color: #b3261e;
    }
</style>

<script>
    // Based on https://codepen.io/marlasdaughter/pen/yGZZLp

    let { color_codes, name } = $props();

    let palette;

</script>

<div class="palette-container">
    <div class="palette-name">{name}</div>
    <div bind:this={palette} class="color-palette">
        {#each color_codes as cc, i}
            <input type="color" bind:value={color_codes[i]} title={cc} />
        {/each}
    </div>
</div>

<style>
    .palette-container {
        display: flex;
        flex-direction: column;
        gap: var(--sp-1);
    }

    .palette-name {
        font-size: var(--text-sm);
        font-weight: 600;
        color: var(--text-primary);
    }

    .color-palette {
        display: flex;
        flex-direction: row;
        flex-wrap: wrap;
        justify-content: flex-start;
        gap: var(--sp-1);
    }

    input[type="color"] {
        width: 28px;
        height: 28px;
        padding: 0;
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-sm);
        background: none;
        transition: border-color 120ms ease;
    }

    input[type="color"]::-webkit-color-swatch-wrapper {
        padding: 0;
    }

    input[type="color"]::-webkit-color-swatch {
        border: none;
        border-radius: var(--radius-sm);
    }

    input[type="color"]:hover {
        cursor: pointer;
        border-color: var(--border-strong);
    }
</style>

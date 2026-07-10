<script>
    import DynamicImage from "../DynamicImage.svelte";
    import { in_japanese } from '../../stores.js';
    import { translate } from '../../lib/i18n.js';

    let { material_path, material_name, material_info, index } = $props();

    let display_name = $state(material_name);
    let display_info = $state(material_info);

    $effect(() => {
        if ($in_japanese) {
            translate("EN", "JA", material_name).then((result) => {
                display_name = result;
            });
            translate("EN", "JA", material_info).then((result) => {
                display_info = result;
            });
        } else {
            display_name = material_name;
            display_info = material_info;
        }
    });

</script>

<div class="card">
    <div class="card-image">
        <DynamicImage imagepath={material_path} alt={material_name} is_draggable={true} size="72px" />
    </div>
    <div class="card-body">
        <h4 class="card-title">{display_name}</h4>
        <p class="card-info">{display_info}</p>
    </div>
</div>

<style>
    .card {
        display: flex;
        flex-direction: row;
        align-items: flex-start;
        gap: var(--sp-2);
        padding: var(--sp-2);
        background: var(--bg-inset);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        transition: border-color 120ms ease;
    }

    .card:hover {
        border-color: var(--border-strong);
    }

    .card-image {
        flex-shrink: 0;
    }

    .card-body {
        flex: 1 1 auto;
        min-width: 0;
        display: flex;
        flex-direction: column;
        gap: var(--sp-1);
    }

    .card-title {
        margin: 0;
        font-size: var(--text-base);
        font-weight: 600;
        color: var(--text-primary);
    }

    .card-info {
        margin: 0;
        font-size: var(--text-sm);
        line-height: 1.5;
        color: var(--text-secondary);
    }
</style>

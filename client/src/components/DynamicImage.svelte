<script>
import Button from "../lib/ui/Button.svelte";
import {transferred_texture_url} from '../stores.js';
import {transferred_textureimg_url} from '../stores.js';
import {transferred_texture_name} from '../stores.js';
import {isDraggingImage} from '../stores.js';
import { viewport } from '../lib/registry.js';
import {in_japanese} from '../stores.js';
import { imageUrl } from '../lib/api.js';

// Displays a server image straight from its static URL. The server
// overwrites generated files in place, so URLs are cache-busted whenever
// the path changes or a refresh is requested.
let {
    imagepath = $bindable(), // Public image path from the server (e.g. "gen_images/...")
    alt, // Alternate text to be displayed
    size = "200px",
    is_draggable = false,
} = $props();

let refresh_token = $state(0);
let imagesource = $derived.by(() => {
    void refresh_token;
    return imageUrl(imagepath, { bust: true });
});

/** Re-derive the src with a fresh cache-buster (the file changed on disk). */
export function getImage() {
    refresh_token += 1;
}

function dragStart(event) {
    if (!is_draggable) {
        event.preventDefault();
        return;
    }
    isDraggingImage.set(true);
    transferred_texture_url.set(imagesource);
    transferred_textureimg_url.set(imagepath);
    transferred_texture_name.set(alt);
}

/** Human-readable texture name; falls back to the file name when the
 *  caller gave no alt text (e.g. the persisted gallery). */
function textureName() {
    if (alt && alt.trim()) return alt;
    const base = (imagepath || '').split('/').pop() || '';
    return base.replace(/\.[^.]+$/, '').replace(/_\d+$/, '').replace(/_/g, ' ') || 'texture';
}

export async function apply_texture() {
    viewport.get()?.applyTexture({
        name: textureName(),
        imagePath: imagepath,
    });
}

</script>

<div class="container" class:draggable={is_draggable} style:width={size} style:height={size}>
    <img
        src={imagesource}
        alt={alt ? alt : "Image"}
        draggable={is_draggable}
        ondragstart={dragStart}
    />
    {#if is_draggable}
        <div class="overlay">
            <Button variant="primary" size="sm" fullWidth onclick={apply_texture}>
                {$in_japanese ? "テクスチャーを貼る" : "Apply Texture"}
            </Button>
        </div>
    {/if}
</div>

<style>
    .container {
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .container.draggable {
        cursor: grab;
    }

    .container.draggable:active {
        cursor: grabbing;
    }

    img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        border-radius: var(--radius-md);
        border: 1px solid var(--border-subtle);
    }

    .overlay {
        position: absolute;
        left: 0;
        right: 0;
        bottom: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: var(--sp-1);
        background: rgba(0, 0, 0, 0.55);
        border-bottom-left-radius: var(--radius-md);
        border-bottom-right-radius: var(--radius-md);
        opacity: 0;
        transition: opacity 120ms ease;
    }

    .container:hover .overlay,
    .container:focus-within .overlay {
        opacity: 1;
    }
</style>

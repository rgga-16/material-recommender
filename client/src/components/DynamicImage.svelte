<script>
import { onMount, onDestroy } from "svelte";
import Spinner from "../lib/ui/Spinner.svelte";
import Button from "../lib/ui/Button.svelte";
import {transferred_texture_url} from '../stores.js';
import {transferred_textureimg_url} from '../stores.js';
import {transferred_texture_name} from '../stores.js';
import {isDraggingImage} from '../stores.js';
import { viewport } from '../lib/registry.js';
import {in_japanese} from '../stores.js';

// This component is a dynamic image component. It should dynamically load an image given its path.
let {
    imagepath = $bindable(), // Image path that will be passed to the server to get the image
    alt, // Alternate text to be displayed
    size = "200px",
    is_draggable = false,
} = $props();

let imagesource = $state(); // Returned image (object URL)
let is_loading = $state(false);

export async function getImage() {
    is_loading = true;
    try {
        const response = await fetch("/get_image", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                "image_data": imagepath,
            }),
        });
        const blob = await response.blob();
        const previous = imagesource;
        imagesource = URL.createObjectURL(blob);
        if (previous) URL.revokeObjectURL(previous);
    } catch (error) {
        console.error(error);
    } finally {
        is_loading = false;
    }
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

export async function apply_texture() {

    transferred_textureimg_url.update(value => {
        value = imagepath;
        return value;
    });
    transferred_texture_url.update(value => {
        value = imagesource;
        return value;
    });
    transferred_texture_name.update(value => {
        value = alt;
        return value;
    });
    viewport.get()?.fullTextureTransferAlgorithm();
}

let previousImagepath = imagepath;

$effect(() => {
    // Track imagepath; skip the very first run since onMount already fetches
    // the initial value. Re-fetch only when it actually changes afterwards.
    if (imagepath !== previousImagepath) {
        previousImagepath = imagepath;
        getImage();
    }
});

onMount(getImage);

onDestroy(() => {
    if (imagesource) URL.revokeObjectURL(imagesource);
});

</script>

<div class="container" class:draggable={is_draggable} style:width={size} style:height={size}>
    {#if is_loading}
        <div class="placeholder">
            <Spinner size={Math.min(32, parseInt(size) || 32)} />
        </div>
    {:else}
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

    .placeholder {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--bg-inset);
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

<script>
import { onMount } from "svelte";
import { Circle } from 'svelte-loading-spinners';
import {transferred_texture_url} from '../stores.js';
import {transferred_textureimg_url} from '../stores.js';
import {transferred_texture_name} from '../stores.js';
import {isDraggingImage} from '../stores.js';

// This component is a dynamic image component. It should dynamically load an image given its path.
export let imagepath; //Image path that will be passed to the server to get the image
export let alt; //Alternate text to be displayed
export let size="200px";
export let is_draggable=false;
let imagesource; //Returned image

let is_loading=false;


export async function getImage() {
    is_loading=true; 
    try {   
        const response = await fetch("/get_image", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                "image_data": imagepath,
            }),
        });
        const blob = await response.blob();
        imagesource = URL.createObjectURL(blob);
    } catch (error) {
        console.error(error);
    } finally {
        is_loading=false;
    }

}

function dragStart(event) {
    if (!is_draggable) {
        event.preventDefault();
        return;
    }
    isDraggingImage.set(true);
    event.dataTransfer.setData("text/plain", event.target.src);
    transferred_texture_url.set(imagesource);
    transferred_textureimg_url.set(imagepath);
    transferred_texture_name.set(alt);
}

$: getImage();

onMount(getImage);

</script>
    {#if is_loading}
        <Circle size="60" color="#FF3E00" unit="px" duration="1s" />
    {:else}
        <img src={imagesource} alt={alt ? alt:"Image"} style="max-width: {size}; max-height:{size}" draggable={is_draggable} on:dragstart={dragStart}>
    {/if}
<style>
    img {
        width: 100%;
        height: 100%;
    }
</style>



<!-- 
    DUMP. OLD CODE.
<script>
    export async function getImage2() {
        is_loading=true;
        const start = performance.now();
        await fetch("/get_image", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                "image_path": imagepath,
            }),
        }).then(response => response.blob())
        .then(blob => {
            const reader = new FileReader();
            reader.onload = () => {
                imagesource = reader.result;
                is_loading=false;
                const end = performance.now();
                console.log("Old getImage() took " + (end - start) + " milliseconds.");
            };
            reader.readAsDataURL(blob);
        }).catch(error => console.error(error));
    }

</script> -->
<script>
import { onMount } from "svelte";
// This component is a dynamic image component. It should dynamically load an image given the URL.
export let imagepath; //Image path that will be passed to the server to get the image
export let alt; //Alternate text to be displayed
let imagesource; //Returned image

async function getImage() {
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
        };
        reader.readAsDataURL(blob);
    }).catch(error => console.error(error));

}

onMount(getImage);

</script>

<img src={imagesource} alt={alt ? alt:"Image"}>

<style>
    img {
        max-width: 100%;
        height: auto;
    }
</style>
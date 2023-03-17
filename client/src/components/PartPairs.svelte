<script>
    import { onMount } from "svelte";
    import DynamicImage from "./DynamicImage.svelte";
    
    export let obj; 
    // export let object_info; 

    export let child_part; 
    export let child_mat_name;
    export let child_mat_finish; 
    export let child_mat_url; 

    export let parent_part; 
    export let parent_mat_name;
    export let parent_mat_finish;
    export let parent_mat_url; 

    
    

    let assembly_feedback=[];

    let currentView=0;
    let viewString = "View suggested attachments";

    let child_image;
    let parent_image; 
    export function updateImages() {
        child_image.getImage();
        parent_image.getImage();
    }

    async function get_assembly_feedback() {
        assembly_feedback=[];

        let partpairs_dict = {
            "object":obj, 
            "child_part":child_part,
            "child_material":object_info[child_part]["mat_name"],
            "parent_part":parent_part,
            "parent_material":parent_mat_name,
        }
        
        const assembly_feedback_response = await fetch("/get_feedback_on_assembly", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(partpairs_dict),
        });

        const assembly_feedback_json = await assembly_feedback_response.json();
        assembly_feedback = await assembly_feedback_json;
    }

    function switchImage() {
        if(currentView===0) {
            currentView = 1;
            viewString = "View parts";
        } else {
            currentView = 0;
            viewString = "View suggested attachments";
        }
    }


</script>

<form on:submit|preventDefault={get_assembly_feedback}>
    <div class="component">
        {#if currentView===0}
            <div class="pairs">
                <div class="material-card">
                    <p> <b> {child_part} </b></p>
                    <DynamicImage bind:this={child_image} imagepath={child_mat_url} alt={child_mat_name} />
                    <p> Material: {child_mat_name}</p>
                </div>
        
                <div id="arrow">
                    <p> ==> </p>
                </div>
                
                <div class="material-card">
                    <p> <b> {parent_part} </b></p>
                    <DynamicImage bind:this={parent_image} imagepath={parent_mat_url} alt={parent_mat_name} />
                    <p> Material: {parent_mat_name}</p>
                </div>
            </div>
        {:else if currentView===1}   
            {#await assembly_feedback}
                <pre> Loading feedback on assembling the {child_part} with the {parent_part}</pre>
            {:then assembly_feedback} 
                <div class="feedback">
                    {#each assembly_feedback as feedback}
                        <h5> {feedback["name"]} </h5>
                        <p> {feedback["reason"]} </p>
                    {/each}
                </div>
            {/await}
        {/if}
        <button> Suggest attachments </button>
        {#if assembly_feedback.length>0}<button on:click|preventDefault={switchImage}> {viewString}</button>{/if}
        
    </div>


</form>

<style>
    .component {
        display:flex;
        flex-direction: column;
        padding: 5px;
        border: 1px solid black; 
        justify-content: center;
        align-items: center;
    }
    .pairs {
        display:flex; 
        flex-direction: row;
        border: 1px solid grey;
        padding: 5px; 
        justify-content: center;
    }

    .material-card {
        border: 1px solid lightgrey; 
        padding: 5px;
        justify-content: center;
        text-align: center;
    }

    img {
        width: 100px;
        height: 100px;
        object-fit: cover;
    }

    #arrow {
        text-align: center;
    }

</style>
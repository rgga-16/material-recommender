<script>
    import { onMount } from "svelte";
    
    export let obj; 
    export let object_info; 

    export let child_part; 
    export let parent_part; 

    let assembly_feedback=[];

    let currentView=0;
    let viewString = "View suggested attachments";

    async function get_assembly_feedback() {
        assembly_feedback=[];

        let partpairs_dict = {
            "object":obj, 
            "child_part":child_part,
            "child_material":object_info[child_part]["mat_name"],
            "parent_part":parent_part,
            "parent_material":object_info[parent_part]["mat_name"],
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

    // onMount(get_assembly_feedback());


</script>

<form on:submit|preventDefault={get_assembly_feedback}>
    <div class="component">
        {#if currentView===0}
            <div class="pairs">
                <div class="material-card">
                    <p> <b> {child_part} </b></p>
                    <img src={object_info[child_part]["mat_image_texture"]} alt={object_info[child_part]["mat_name"]} />
                    <p> Material: {object_info[child_part]["mat_name"]}</p>
                </div>
        
                <div id="arrow">
                    <p> ==> </p>
                </div>
                
                <div class="material-card">
                    <p> <b> {parent_part} </b></p>
                    <img src={object_info[parent_part]["mat_image_texture"]} alt={object_info[parent_part]["mat_name"]} />
                    <p> Material: {object_info[parent_part]["mat_name"]}</p>
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
<script>
    import {onMount} from 'svelte';

    import MaterialCard from '../SuggestModule/MaterialCard.svelte';
    import ColorPalette from '../SuggestModule/ColorPalette.svelte';
    import {saved_color_palettes} from '../../stores.js';
    import {chatbot_input_message} from '../../stores.js';

    import {actions_panel_tab} from '../../stores.js';
    import {generate_tab_page} from '../../stores.js';
    import {createEventDispatcher} from 'svelte';


    const dispatch = createEventDispatcher();

    let inputMessage = '';
    let use_internet=false;
    
    let messages = [];
    /*
    Let the message dictionary format be:
    {
        "message": "Hello",
        "role": "user",
        "type": "regular" OR "suggested_materials" OR "suggested_color palettes"
        "content": [list of suggested materials or color palettes] if type is "suggested_materials" or "suggested_color palettes"
    }
    */

    let suggested_material_queries = [
        "What are some wood materials that are generally low-cost?",
        "What materials would you suggest that are eco-friendly and sustainable?",
        "What materials do you recommend for a modern-style interior bedroom?",
        "Can you suggest materials that are durable in a high-traffic commercial space?",
        "Can you suggest materials that can be locally sourced in [location]?"
    ];

    let expanded_suggested_questions=false;
    function expand() {
        expanded_suggested_questions = !expanded_suggested_questions;
    }
    let is_loading=false;

    async function suggest_materials() {
        if (inputMessage.trim() === '') {
            alert("Please enter a query.");
            return;
        }
        messages.push({
            "message": inputMessage,
            "role": "user",
            "type": "regular"
        });
        messages = messages;

        const response = await fetch("/suggest_materials", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                "prompt": inputMessage,
                "role":"user",
                "use_internet": use_internet
            }),
        });
        const json = await response.json();
        inputMessage = '';

        let intro_text = json["intro_text"];
        let role = json["role"];
        let suggested_materials = json["suggested_materials"];
        console.log(suggested_materials);

        let message_type = "suggested_materials";
        messages.push({
            "message": intro_text,
            "role": role,
            "type": message_type,
            "content": suggested_materials
        });
        messages = messages;
    }

    async function suggest_color_palettes() {
        if (inputMessage.trim() === '') {
            alert("Please enter a query.");
            return;
        }

        messages.push({
            "message": inputMessage,
            "role": "user",
            "type": "regular"
        });
        messages = messages;

        const response = await fetch("/suggest_colors", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                "prompt": inputMessage,
                "role":"user",
                "use_internet": use_internet
            }),
        });
        const json = await response.json();
        inputMessage = '';

        let intro_text = json["intro_text"];
        let role = json["role"];
        let suggested_color_palettes = json["suggested_color_palettes"];
        console.log(suggested_color_palettes);

        let message_type = "suggested_color_palettes";
        messages.push({
            "message": intro_text,
            "role": role,
            "type": message_type,
            "content": suggested_color_palettes
        });
        messages = messages;
    }

    function saveColorPalette(color_palette) {
        let dict = {
            name: color_palette["name"],
            palette: color_palette["codes"]
        }
        saved_color_palettes.update(lst => lst.concat(dict));
        alert("Color palette saved!");
    }

    async function query() {

        if (inputMessage.trim() === '') {
            return;
        }

        messages.push({
            "message": inputMessage,
            "role": "user"
        });
        messages = messages;

        const response = await fetch("/query", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                "prompt": inputMessage,
                "role":"user",
            }),
        });
        const json = await response.json();

        let message= json["response"];
        let role = json["role"];

        messages.push({
            "message": message,
            "role": role
        });
        messages = messages;

        console.log(messages);
        inputMessage = '';

    }

    async function init_query() {
        const response = await fetch('./init_query');
        const json = await response.json();
        let message = json["response"];
        let role = json["role"];
        messages.push({
            "message": message,
            "role": role
        });
        messages = messages;
        console.log(messages);
    }

    function handleInput(event) {
        inputMessage = event.target.innerText;
        const textarea = document.getElementById("textarea");
        textarea.value=event.target.innerText;
    }
    
    async function brainstorm_material_queries() {
        const response = await fetch('./brainstorm_material_queries');
        const json = await response.json(); 
        suggested_material_queries = json['prompts']
        console.log(suggested_material_queries)
    }

    function generate(material_name) {
        actions_panel_tab.set("generate");
        generate_tab_page.set(0);
        dispatch('proceedToGenerate',material_name)
    }

    onMount(async () => { //UNCOMMENT ME WHEN YOU'RE TESTING THE CHATBOT
        await init_query();

        // If the chatbot_input_message, a global store, is updated, update the inputMessage variable and the text in the textbox message area.
        chatbot_input_message.subscribe(value => {
            inputMessage = value;
            const textarea = document.getElementById("textarea");
            textarea.innerHTML='';
            textarea.value=inputMessage;
        });
    });

</script>

<div class="messages">
    {#each messages as message}
        <div class="message">
            <div class="{message.role}">
                <strong>{message.role}: </strong>
                <p> {message.message} </p>
                {#if message.type == "suggested_materials"}
                    {#each message.content as m, i}
                        <MaterialCard material_path={m["filepath"]} material_name={m["name"]} material_info={m["reason"]} index={i}/>
                        <button 
                            on:click|preventDefault={()=> generate(m["name"])}
                            style="align-items: center; justify-content: center; cursor: pointer;"
                        >
                            Generate
                            <img src="./logos/magic-wand-svgrepo-com.svg" style="width:25px; height:25px; align-items: center; justify-content: center;" alt="Generate">
                        </button>
                    {/each}
                
                {:else if message.type=="suggested_color_palettes"}
                    <ol>
                        {#each message.content as m,i}
                            <li> 
                                <div class="color-card">
                                    <ColorPalette name={m["name"]} color_codes={m["codes"]} />
                                </div>
                                <button on:click={()=>saveColorPalette(m)}> Save Palette </button>
                                <p> {m["description"]} </p>
                            </li>
                        {/each}
                    </ol>
                {/if}
            </div>
        </div>
    {/each}
</div>



<div class="message-input">
    <div class="floating-div" class:expanded={expanded_suggested_questions===true}>
        <div class=header> 
            <!-- svelte-ignore a11y-click-events-have-key-events -->
            <strong on:click={() => expand()} style="cursor:pointer;"> Suggested Questions </strong> 
            {#if expanded_suggested_questions===true}
                <!-- svelte-ignore a11y-click-events-have-key-events -->
                <img on:click={() => expand()}  src="./logos/down-arrow-svgrepo-com.svg" style="width:25px; height: 25px;cursor:pointer;" alt="Collapse">
            {:else}
                <!-- svelte-ignore a11y-click-events-have-key-events -->
                <img on:click={() => expand()} src="./logos/up-arrow-svgrepo-com.svg" style="width:25px; height: 25px;cursor:pointer;" alt="Expand">
            {/if}
        </div>
        {#if expanded_suggested_questions===false}
                {suggested_material_queries[0].slice(0, 20)}... + {suggested_material_queries.length-1} more
        {:else}
            <div class="body">
                <ul>
                    {#each suggested_material_queries as query}
                        <!-- svelte-ignore a11y-click-events-have-key-events -->   
                        <li on:click={handleInput} style="cursor:pointer;"> {query} </li>
                    {/each}
                </ul>
            </div>
            <div class="footer">
                <button on:click|preventDefault={()=>brainstorm_material_queries()}> Brainstorm questions! </button>
            </div>
        {/if}
    </div>
    <textarea style="width:100%;" bind:value="{inputMessage}" on:keydown="{e => e.key === 'Enter' && suggest_materials()}" placeholder="Type your queries for materials or color palettes here.." id="textarea"></textarea>
    <label>
        <input type="checkbox" bind:checked={use_internet} >
        Use web search
    </label>
    <button on:click|preventDefault={()=>suggest_materials()}>Suggest Materials</button>    
    <button on:click|preventDefault={()=>suggest_color_palettes()}>Suggest Colors</button>   
    
</div>

<style>

    .floating-div {
        padding: 10px;
        position: absolute;
        display:flex; 
        flex-direction: column;
        top: -160px;
        right: 0;
        left: 0;
        bottom:0;
        margin: auto;
        width: 90%;
        height: 60px;
        background-color: white;
        border: 1px solid #E0E0E0;
        border-radius: 20px;
        box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);
        z-index: 1;
        gap: 5px;
    }

    .floating-div .header {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
        width: 100%;
        /* height: 10%; */
    }

    .floating-div .body {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
        width: 100%;
        height: 100%;
        overflow-y: scroll;
    }

    .body li:hover {
        color: blue;
    }

    .floating-div .footer {
        display: flex;
        flex-direction: row;
        justify-content: center;
        align-items: center;
    }

    .floating-div.expanded {
        /* overflow-y: scroll; */
        top: -360px;
        height: 300%;
    }

    .message-input {
        position: relative;
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
        padding: 10px;
        width: 100%;
        height: 10%;
    }


    .messages {
        background-color: white;
        display: flex;
        flex-direction: column;
        height: 90%;
        width: 100%;
        overflow-y: scroll;
        padding: 10px;
    }
    .user {
		background-color: white;
		
	}

	.assistant {
		background-color: lightgray;
	}

    .suggested_materials {
        background-color: lightgray;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
        gap: 5px;
    }

    .color-card {
        border: 1px solid black;
        padding: 5px;
        height: 180%;
        width: 100%;
        margin-bottom: 5px;
    }

</style>
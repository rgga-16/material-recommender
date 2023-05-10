<script>
    import {onMount} from 'svelte';
    import MaterialCard from '../SuggestModule/MaterialCard.svelte';
    import {actions_panel_tab} from '../../stores.js';
    import {generate_tab_page} from '../../stores.js';

    let inputMessage = '';
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

    async function suggest_materials() {

        messages.push({
            "message": inputMessage,
            "role": "user",
            "type": "regular"
        });
        messages = messages;

        if (inputMessage.trim() === '') {
            return;
        }

        const response = await fetch("/suggest_materials", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                "prompt": inputMessage,
                "role":"user",
            }),
        });
        const json = await response.json();

        let intro_text = json["intro_text"];
        let role = json["role"];
        let suggested_materials = json["suggested_materials"];
        console.log(suggested_materials);

        // HOW TO DISPLAY THE SUGGESTED MATERIALS AND IMAGES AAAA
        let message_type = "suggested_materials";
        messages.push({
            "message": intro_text,
            "role": role,
            "type": message_type,
            "content": suggested_materials
        });
        messages = messages;

        // console.log(messages);
        inputMessage = '';
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

    onMount(async () => {
        await init_query();
    });

</script>

<div class="messages">
    {#each messages as message}
        <div class="message">
            <div class="{message.role}">
                <strong>{message.role}: </strong>
                <p>
                    {message.message}
                </p>
                {#if message.type == "suggested_materials"}
                    {#each message.content as m, i}
                        <MaterialCard material_path={m["filepath"]} material_name={m["name"]} material_info={m["reason"]} index={i}/>
                        <!-- <button on:click={()=>proceed_to_generate(suggested_materials[selected_material_index]["name"] + " " + selected_material_type)}> Generate </button> -->
                    {/each}
                {/if}

                <!-- {#if message.type == "suggested_color palettes"}
                    {#each message.content as color_palette}
                        <ColorPaletteCard color_palette_path={color_palette.color_palette_path} color_palette_name={color_palette.color_palette_name} color_palette_info={color_palette.color_palette_info} index={color_palette.index}/>
                    {/each}
                    
                {/if} -->

            </div>
        </div>
    {/each}
</div>

<div class="message-input">
    <input type="text" bind:value="{inputMessage}" on:keydown="{e => e.key === 'Enter' && query()}" placeholder="Type a message"> 
    <button on:click|preventDefault={()=>suggest_materials()}>Send</button>    
</div>


<style>

    .message-input {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
        padding: 10px;
        width: 100%;
    }


    .messages {
        background-color: white;
        display: flex;
        flex-direction: column;
        height: 100%;
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

</style>
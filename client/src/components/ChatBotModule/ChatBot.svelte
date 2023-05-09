<script>
    import {onMount} from 'svelte';

    let inputMessage = '';
    let messages = [];

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
            </div>
        </div>
    {/each}
</div>

<div class="message-input">
    <input type="text" bind:value="{inputMessage}" on:keydown="{e => e.key === 'Enter' && query()}" placeholder="Type a message"> 
    <button on:click|preventDefault={()=>query()}>Send</button>    
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


    div.messages {
        background-color: white;
        display: flex;
        flex-direction: column;
        height: 100%;
        width: 100%;
        overflow-y: scroll;
        padding: 10px;
    }
    div.user {
		background-color: white;
		
	}

	div.assistant {
		background-color: lightgray;
	}

</style>
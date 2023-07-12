<script>
    import Generate from "./GenerationModule/Generate.svelte";
    import SuggestMaterials from "./SuggestModule/SuggestMaterials.svelte";
    import SuggestColors from "./SuggestModule/SuggestColors.svelte";
    import ChatBot from "./ChatBotModule/ChatBot.svelte";
    import {actions_panel_tab} from '../stores.js';
    import {use_chatgpt} from '../stores.js';
    import {onMount} from 'svelte';
    import {generate_module} from '../stores.js';
    import {get} from 'svelte/store';
    import {in_japanese} from '../stores.js';
    let japanese;
    in_japanese.subscribe(value => {
        japanese = value;
    });

    export let onCallUpdateCurrentRendering;
    let generate;

    function callUpdateCurrentRendering() {
        onCallUpdateCurrentRendering();
    }
    
    let activeTab;
    actions_panel_tab.subscribe(value => {
        activeTab = value;
    });

    function switchTab(tab) {
      actions_panel_tab.set(tab);
    }

    onMount(() => {
      generate_module.set(generate);
    });

    

    
</script>

<div class="actions-panel">
  <div class="w3-bar w3-grey tabs">
    <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='generate'} on:click={()=>switchTab('generate')} id="generate-btn">
      {japanese ? "生成する" : "Generate"}
    </button>
    {#if get(use_chatgpt)}
    <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='chatbot'} on:click={()=>switchTab('chatbot')} id="chatbot-btn">
      {japanese ? "チャットボット" : "ChatBot"}
    </button>
    {/if}
    <!-- <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='suggest_materials'} on:click={()=>switchTab('suggest_materials')} id="suggest-materials-btn">Suggest Materials</button>
    <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='suggest_colors'} on:click={()=>switchTab('suggest_colors')} id="suggest-colors-btn">Suggest Colors</button> -->
  </div>
  
  <div class='tab-content'  class:active={activeTab==='generate'} id="generate">
    <Generate onCallUpdateCurrentRendering={callUpdateCurrentRendering} bind:this={generate} />
  </div> 

  {#if get(use_chatgpt)}
    <div class="tab-content" class:active={activeTab==='chatbot'} id="chatbot">
      <ChatBot on:proceedToGenerate={arg => {
        generate.empty_keywordlists();
        generate.generate_textures(arg.detail);
        generate.reset_page(); }}/>
    </div>
  {/if}

</div>
      
<style>

  .actions-panel{
    display:flex;
    flex-direction: column;
    height: inherit;
  }

  .tabs{
    display:flex; 
    flex-direction: row;
  }

  .tab-btn {
    height:100%;
    border: black 1px solid;
  }

	.tab-btn.active {
		background-color: rgb(89, 185, 218);
	}

  .tab-btn.active:hover {
		background-color: rgb(89, 185, 218);
	}
  
	.tab-content {
		display: none;
	}
  
	.tab-content.active {
		display: flex;
    flex-direction: column;
    height: 100%;
    width:100%;
    padding: 5px;
    overflow: auto; 
	}
</style>



  <!-- <div class='tab-content' class:active={activeTab==='suggest_materials'} id="suggest_materials">
    <SuggestMaterials on:proceedToGenerate={arg => {
      generate.generate_textures(arg.detail);
      generate.reset_page();
    }}/>
  </div> -->

  <!-- <div class='tab-content' class:active={activeTab==='suggest_colors'} id="suggest_colors">
    <SuggestColors />
  </div> -->
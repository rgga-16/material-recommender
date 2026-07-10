<script>
    // Tool-panel body. Tab switching now lives in the App shell's icon rail,
    // which drives the shared actions_panel_tab store.
    import Generate from "./GenerationModule/Generate.svelte";
    import PresetMaterials from "./NewModules/PresetMaterials.svelte";
    import UploadPanel from "./NewModules/UploadPanel.svelte";
    import AutoStyle from "./NewModules/AutoStyle.svelte";
    import ChatBot from "./ChatBotModule/ChatBot.svelte";
    import {actions_panel_tab} from '../stores.js';
    import {use_chatgpt} from '../stores.js';
    import {get} from 'svelte/store';

    export let onCallUpdateCurrentRendering;
    let generate;

    function callUpdateCurrentRendering() {
        onCallUpdateCurrentRendering();
    }

    let activeTab;
    actions_panel_tab.subscribe(value => {
        activeTab = value;
    });
</script>

<div class="actions-panel">
  <div class='tab-content' class:active={activeTab==='generate'} id="generate">
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

  <div class='tab-content' class:active={activeTab==='mat_lib'} id="mat_lib">
    <PresetMaterials/>
  </div>

  <div class='tab-content' class:active={activeTab==='upload'} id="upload">
    <UploadPanel/>
  </div>

  <div class='tab-content' class:active={activeTab==='auto_style'} id="auto_style">
    <AutoStyle/>
  </div>
</div>

<style>
  .actions-panel{
    display:flex;
    flex-direction: column;
    height: 100%;
  }

	.tab-content {
		display: none;
	}

	.tab-content.active {
		display: flex;
    flex-direction: column;
    height: 100%;
    width:100%;
    padding: var(--sp-3);
    overflow: auto;
	}
</style>

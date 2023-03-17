<script>
    import Generate from "./GenerationModule/Generate.svelte";
    import SuggestMaterials from "./SuggestModule/SuggestMaterials.svelte";
    import SuggestColors from "./SuggestModule/SuggestColors.svelte";
    
    let activeTab = 'generate';
    function switchTab(tab) {
        activeTab = tab;
    }

    
</script>

<div class="actions-panel">
  <div class="w3-bar w3-grey tabs">
    <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='generate'} on:click={()=>switchTab('generate')} id="generate-btn">Generate</button>
    <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='suggest_materials'} on:click={()=>switchTab('suggest_materials')} id="suggest-materials-btn">Suggest Materials</button>
    <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='suggest_colors'} on:click={()=>switchTab('suggest_colors')} id="suggest-colors-btn">Suggest Colors</button>
  </div>
  
  <div class='tab-content'  class:active={activeTab==='generate'} id="generate">
    <Generate />
  </div> 

  <div class='tab-content' class:active={activeTab==='suggest_materials'} id="suggest_materials">
    <SuggestMaterials />
  </div>

  <div class='tab-content' class:active={activeTab==='suggest_colors'} id="suggest_colors">
    <SuggestColors />
  </div>

</div>
      
  <style>

  .actions-panel{
    display:flex;
    flex-direction: column;
    height: inherit;
  }

  .tab-btn {
    height:100%;
  }

	.tab-btn.active {
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
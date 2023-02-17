<script>
    import Generate from "./Generate.svelte";
    import Suggest from "./Suggest.svelte";
    
    let activeTab = 'tab1-content';
  
    function switchTab(tab) {
        activeTab = tab;
    }

    
</script>

    <div class="user-interface">
      <div class="w3-bar w3-grey tabs">
        <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='tab1-content'} on:click={()=>switchTab('tab1-content')} id="tab1-btn">Generate</button>
        <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='tab2-content'} on:click={()=>switchTab('tab2-content')} id="tab2-btn">Suggest</button>
        <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='tab3-content'} on:click={()=>switchTab('tab3-content')} id="tab3-btn">Feedback</button>
      </div>
      
      <div class='tab-content'  class:active={activeTab==='tab1-content'} id="tab1-content">
        <Generate />
      </div> 

      <div class='tab-content' class:active={activeTab==='tab2-content'} id="tab2-content">
        <Suggest />
      </div>

      <div class='tab-content' class:active={activeTab==='tab3-content'} id="tab3-content">
        <h2>Tab 3 Content</h2>
        <p>Sed facilisis mi at est commodo, in fringilla metus egestas.</p>
      </div> 
    </div>
      
  <style>
  
  /* .tabs {
    display: flex;
    
  } */
  
  .user-interface{
    display:flex;
    flex-direction: column;
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
		display: block;
    padding: 1rem;
	}
  </style>
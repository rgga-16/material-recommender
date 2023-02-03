<script>
    import Generate from "./Generate.svelte";
    
    let activeTab = 'tab1-content';
    const active_string = ' active';
  
    function switchTab(tab) {
        activeTab = tab;
        console.log(activeTab);
    }

    
</script>


    <h2>watda</h2>
    <div class="tab-group">
      <button class={activeTab==='tab1-content' ? 'tab-btn active':'tab-btn'} on:click={()=>switchTab('tab1-content')} id="tab1-btn">Generate</button>
      <button class={activeTab==='tab2-content' ? 'tab-btn active':'tab-btn'} on:click={()=>switchTab('tab2-content')} id="tab2-btn">Suggest</button>
      <button class={activeTab==='tab3-content' ? 'tab-btn active':'tab-btn'} on:click={()=>switchTab('tab3-content')} id="tab3-btn">Feedback</button>
    
      <div  class={activeTab==='tab1-content' ? 'tab-content active': 'tab-content'} id="tab1-content">
        <Generate />
      </div> 

      <div class={activeTab==='tab2-content' ? 'tab-content active': 'tab-content'} id="tab2-content">
        <h2>Suggest</h2>
        <p>Donec blandit velit vel ipsum malesuada, eu congue nisl bibendum.</p>
      </div>

      <div class={activeTab==='tab3-content' ? 'tab-content active': 'tab-content'} id="tab3-content">
        <h2>Tab 3 Content</h2>
        <p>Sed facilisis mi at est commodo, in fringilla metus egestas.</p>
      </div> 

    </div>

  <style>
    

	.tab-group {
		width: 100%;
		margin: 0 auto;
  	}
  
	.tab-btn {
		background-color: rgb(148, 148, 148);
		border: none;
		color: black;
		cursor: pointer;
		display: inline-block;
		padding: 14px 16px;
		text-align: center;
		width: 33.33%;
	}
  
	.tab-btn.active {
		background-color: rgb(89, 185, 218);
	}
  
	.tab-content {
		display: none;
		padding: 16px;
	}
  
	.tab-content.active {
		display: block;
	}
  </style>
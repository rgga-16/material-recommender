
<script>
    import PreviewCard from "./PreviewCard.svelte";
  
      
      export let pairs;
      export let selected_texturepaths=[]; 
  </script>
  
  <div class="image-grid">
      {#each pairs as pair, i}
          <label class="preview-card" class:selected={selected_texturepaths.includes(pair.texture)}>
              <input type=checkbox bind:group={selected_texturepaths} name="option" value={pair.texture} >
              <PreviewCard texture={pair.texture} rendering={pair.rendering} info={pair.info} index={i}/>
          </label>
      {/each} 
      
  </div>
  
  <style>
      .image-grid input[type="checkbox"] {
          opacity: 0;
          position: fixed;
          width:0; 
      } 
  
      .image-grid {
          width:100%;
          max-width:900px;
          margin:0 auto;
          text-align:left;
      }
  
      .preview-card {
          /* display:flex;  */
          flex-direction: row;
          border: 1px solid grey;
          /* padding:5px; 
          max-width: 50%; */
          display: inline-block;
          /* height: 170px;
          width: 170px; */
          margin:5px;
          background-color:lightblue;
      }
  
      .preview-card:hover {
          border: 3px solid grey;
      }
  
      .selected {
          border: 3px solid blue;
      }
  
      
  </style>
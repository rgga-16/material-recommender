<script>
    import DynamicImage from "../DynamicImage.svelte";
    import SvelteMarkdown from 'svelte-markdown';
    export let material_path;
    export let material_name;
    export let material_info; 
    export let index;

    let is_selected=false;

    function copyText(text) {
        navigator.clipboard.writeText(text);
    }

</script>

<div class="card">
    <h3> {material_name} </h3>
    <div class="card-body">
        <div class="image-container">
            <DynamicImage imagepath={material_path} alt={material_name} is_draggable={true} />
        </div>
        <div class="text-container">
          <SvelteMarkdown source={material_info} />
            <!-- <p>{material_info}</p> -->
        </div>
    </div>
    <!-- <button on:click={copyText}>Copy to clipboard</button> -->
</div>

<style>
    .card {
      display: flex;
      flex-direction: column;
      background-color: #fff;
      border: 1px solid #ccc;
      border-radius: 5px;
      padding: 20px;
      background-color: inherit;
    }
  
    .card h3 {
      margin: 0 0 10px 0;
      font-size: 1.5rem;
    }
  
    .card-body {
      display: flex;
      flex-wrap: wrap;
    }
  
    .image-container {
      flex: 1 1 40%;
    }
  
    .image-container img {
      max-width: 100%;
      height: auto;
      display: block;
      margin: 0 auto;
    }
  
    .text-container {
      flex: 1 1 60%;
      padding: 0 20px;
    }
  
    button {
      background-color: #007bff;
      color: #fff;
      border: none;
      border-radius: 5px;
      padding: 10px 20px;
      margin-top: 20px;
      cursor: pointer;
    }
  
    button:hover {
      background-color: #0056b3;
    }
  </style>
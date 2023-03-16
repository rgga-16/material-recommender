<script>
    import DynamicImage from "./DynamicImage.svelte";
    
    export let part_name;
    // export let part_info;

    export let material_name; 
    export let material_finish; 
    export let material_url;


    // let material_name = part_info["mat_name"];
    // let material_finish = part_info["mat_finish"];
    // let material_url = part_info["mat_image_texture"];

    export let image;
    export function updateImage() {
      image.getImage();
    }
</script>

<div class="card">
    <DynamicImage bind:this={image} imagepath={material_url} alt={material_name} />
    <div class="texture-details">
      <div>
          <div class="texture-name">{material_name}</div>
          <div>{material_finish}</div>
      </div>
      <div><b>{part_name}</b></div>
    </div>
</div>

<style>
    .card {
      display: flex;
      flex-direction: column;
      margin: 1rem;
      max-width: 300px;
      border: 1px solid black;
      padding: 5px; 
    }
    
    .texture-image {
      width: 100%;
      height: 200px;
      object-fit: cover;
    }
    
    .texture-details {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 0.5rem;
      font-size: 0.8rem;
    }
    
    .texture-name {
      font-weight: bold;
    }
  </style>
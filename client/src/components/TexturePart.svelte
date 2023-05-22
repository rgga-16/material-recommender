<script>
    import DynamicImage from "./DynamicImage.svelte";
    import NumberSpinner from "svelte-number-spinner";
    import RangeSlider from "svelte-range-slider-pips";
    import {onMount} from 'svelte';

    import {selected_objs_and_parts} from '../stores.js';
    
    export let part_name;

    export let material_name; 
    export let material_finish; 
    export let material_url;
    
    export let index;
    let material;
    let opacity=[0.5];
    let roughness=[0.5]
    let metalness=[0.5];
    let isTransparent=false;

    let translationX = 0; 
    let translationY = 0;
    let rotation= 0; 
    let scale = 1;
    $:scaleX = scale; 
    $:scaleY =  scale; 

    let sel_objs_and_parts;
    selected_objs_and_parts.subscribe(value => {
      sel_objs_and_parts = value;
    });


    let image;
    export function updateImage() {
      image.getImage();
    }

    onMount(async () => {
      material = sel_objs_and_parts[index].model.children[0].material;
      opacity = [material.opacity];
      roughness = [material.roughness]; 
      metalness = [material.metalness];
      isTransparent = material.transparent;

      translationX = material.map.offset.x;
      translationY = material.map.offset.y;
      rotation = material.map.rotation;
      scaleX = material.map.repeat.x;
      scaleY = material.map.repeat.y;

    });

    function adjustMap(map) {
      map.offset.x = translationX;
      map.offset.y = translationY;
      map.rotation = rotation;
      map.repeat.x = scaleX;
      map.repeat.y = scaleY;
    }

    function fook() {
      selected_objs_and_parts.update(value => {
        value[index].model.children[0].material.transparent= true;
        value[index].model.children[0].material.opacity = opacity[0];
        value[index].model.children[0].material.roughness = roughness[0];
        value[index].model.children[0].material.metalness = metalness[0];

        adjustMap(value[index].model.children[0].material.map);
        if (value[index].model.children[0].material.normalMap) {
          adjustMap(value[index].model.children[0].material.normalMap);
        }
        if (value[index].model.children[0].material.aoMap) {
          adjustMap(value[index].model.children[0].material.aoMap);
        }
        if (value[index].model.children[0].material.alphaMap) {
          adjustMap(value[index].model.children[0].material.alphaMap);
        }
        if(value[index].model.children[0].material.emissiveMap) {
          adjustMap(value[index].model.children[0].material.emissiveMap);
        }
        if (value[index].model.children[0].material.lightMap) {
          adjustMap(value[index].model.children[0].material.lightMap);
        }
        if(value[index].model.children[0].material.metalnessMap) {
          adjustMap(value[index].model.children[0].material.metalnessMap);
        }
        if (value[index].model.children[0].material.bumpMap) {
          adjustMap(value[index].model.children[0].material.bumpMap);
        }
        if(value[index].model.children[0].material.displacementMap) {
          adjustMap(value[index].model.children[0].material.displacementMap);
        }
        if(value[index].model.children[0].material.envMap) {
          adjustMap(value[index].model.children[0].material.envMap);
        }
        if(value[index].model.children[0].material.normalMap) {
          adjustMap(value[index].model.children[0].material.normalMap);
        }
        if (value[index].model.children[0].material.roughnessMap) {
          adjustMap(value[index].model.children[0].material.roughnessMap);
        }
        

        // value[index].model.children[0].material.map.offset.x = translationX;
        // value[index].model.children[0].material.map.offset.y = translationY;  
        // value[index].model.children[0].material.map.rotation = rotation;
        // value[index].model.children[0].material.map.repeat.x = scaleX;
        // value[index].model.children[0].material.map.repeat.y = scaleY;
        return value;
      });
      // console.log(sel_objs_and_parts[index].model.children[0].material);
    }

</script>

<div class="card container">
  <div><b>{part_name}</b></div>  
  <DynamicImage bind:this={image} imagepath={material_url} alt={material_name} size={"200px"}/>
  <div id="texture-details">
        <div class="texture-name">Material: {material_name}</div>
        <div>Material finish: {material_finish}</div>
  </div>

  <div class="card">
    <h5><b>Adjust Finish</b></h5> 
    <div class="control">
      <!-- <span>Is Transparent?: </span> 
      <input type="checkbox" id="transparency" bind:checked={isTransparent} on:change={fook} /> -->
      <span>Opacity: </span>
      <div style="width:100%; align-items:inherit; justify-content:inherit;"> 
        <RangeSlider on:change={fook} bind:values={opacity} min={0} max={1} step={0.1} float={true} pips/> 
      </div>
    </div>
    <div class="control">
      <span>Roughness: </span>
      <div style="width:100%; align-items:inherit; justify-content:inherit;"> 
        <RangeSlider on:change={fook} bind:values={roughness} min={0} max={1} step={0.1} float={true} pips/> 
      </div>
    </div>
    <div class="control">
      <span>Metalness: </span>
      <div style="width:100%; align-items:inherit; justify-content:inherit;"> 
        <RangeSlider on:change={fook} bind:values={metalness} min={0} max={1} step={0.1} float={true} pips/> 
      </div>
    </div>
    
  </div>
  <div class="card">
    <h5><b>Adjust Texture Orientation</b></h5>

    <div class="card container">
      <h6> <b> Location </b></h6>
      <div class="control">
        <span>X:</span>
        <NumberSpinner on:change={fook} bind:value={translationX} min=0.0 max=1 step=0.01 decimals=2 precision=0.01/>
      </div>
      <div class="control">
        <span>Y:</span>
        <NumberSpinner on:change={fook} bind:value={translationY} min=0.0 max=1 step=0.01 decimals=1 precision=0.01/>
      </div>
    </div>
    <div class="card container">
      <h6> <b> Rotation </b></h6>
      <div class="control">
        <span>Z: </span>
        <NumberSpinner on:change={fook} bind:value={rotation} min=0.0 max=6.28 step=0.01 decimals=1 precision=0.01/>
      </div>
    </div>
    <div class="card container">
      <div class="control">
        <span>X & Y: </span>
        <NumberSpinner on:change={fook} bind:value={scale} min=0.0 max=5 step=0.01 decimals=1 precision=0.01/>
      </div>
      <div class="control">
        <span>X: </span>
        <NumberSpinner on:change={fook} bind:value={scaleX} min=0.0 max=5 step=0.01 decimals=1 precision=0.01/>
      </div>
      <div class="control">
        <span>Y: </span>
        <NumberSpinner on:change={fook} bind:value={scaleY} min=0.0 max=5 step=0.01 decimals=1 precision=0.01/>
      </div>
    </div>
    


  </div>


</div>

<style>
    .container {
      border: 1px solid black;
    }

    .card {
      display: flex;
      flex-direction: column;
      padding: 5px; 
      justify-content: center;
      align-items: center;
      gap: 5px;
      width: 100%;
    }

    .control {
      display:flex; 
      flex-direction: row;
      align-items: center;
      justify-content: center;
      gap: 5px;
      width: 100%;
    }

    
    #texture-details {
      display: flex;
      flex-direction:column;
      justify-content: space-between;
      align-items: center;
      font-size: 0.8rem;
    }
/* 
    #color-details {
      display: flex;
      flex-direction:column;
      justify-content: space-between;
      align-items: center;
      margin-top: 0.5rem;
      font-size: 0.8rem;
    } */

    
    
    .texture-name {
      font-weight: bold;
    }
  </style>
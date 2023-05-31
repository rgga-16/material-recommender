<script>
    import DynamicImage from "./DynamicImage.svelte";
    import NumberSpinner from "svelte-number-spinner";
    import RangeSlider from "svelte-range-slider-pips";
    import {onMount} from 'svelte';

    import {selected_objs_and_parts} from '../stores.js';
    import {saved_color_palettes} from "../stores.js";
    import {chatbot_input_message} from "../stores.js";
    import {actions_panel_tab} from '../stores.js';

    import {createEventDispatcher} from 'svelte';

    import {curr_texture_parts} from '../stores.js';


    let current_texture_parts;
    curr_texture_parts.subscribe(value => {
      current_texture_parts = value;
    });
    
    export let part_name;
    export let part_parent_name;

    export let material_name; 
    export let material_finish; 
    export let material_url;
    export let material_color=null; //Color code of the material


    /**
     * parents = [
     *  (object, part)
     * 
     * ]
     */
    export let parents = []; //List of parts that this part is attached to.
    let material_color_palette = null;

    if (material_color) {
      material_color_palette = {
        name: 'Custom', 
        palette: [
          material_color,
          "#FFFFFF",
          "#FFFFFF",
          "#FFFFFF",
          "#FFFFFF",
        ]
      };
    }
    
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

    let palettes=[]; 
    let selected_palette_idx=0;
    saved_color_palettes.subscribe(value => {
      palettes=value;
      // selected_palette_idx=0;
    });

    let selected_swatch_idx = undefined;
    const no_color = {name: 'No Color', code: '#FFFFFF'}

    let isOpen=false;
    function toggleDropDown() {
        isOpen = !isOpen;
    }

    let image;
    export function updateImage() {
      image.getImage();
    }
    console.log(parents);


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


    function updateFinish() {
      selected_objs_and_parts.update(value => {
        value[index].model.children[0].material.transparent= true;
        value[index].model.children[0].material.opacity = opacity[0];
        value[index].model.children[0].material.roughness = roughness[0];
        value[index].model.children[0].material.metalness = metalness[0];
        return value;
      });
    }

    function updateTextureMapOrientation() {
      selected_objs_and_parts.update(value => {
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
        return value;
      });

    }

    function updateColor() {
      let color = palettes[selected_palette_idx]['palette'][selected_swatch_idx];
      console.log(selected_palette_idx);
      console.log(color);
      const hexNumber = parseInt(color.substring(1), 16);
      console.log(hexNumber);

      selected_objs_and_parts.update(value => {
        value[index].model.children[0].material.color.setHex(hexNumber);
        return value;
      });
    }

    function suggestSimilarMaterials() {
      let query = "Can you suggest similar materials to " + material_name + " for a " + part_parent_name + " " + part_name + "?";
      actions_panel_tab.set("chatbot");
      chatbot_input_message.set(query);
      // generate_tab_page.set(0);
    }

    let feedback =undefined;
    async function requestMaterialFeedback() {
      
      let attached_parts = [];
      for (const p in parents) {
        const obj = p[0];
        const part = p[1];
        const attached_part_material = current_texture_parts[obj][part]['mat_name'];
        attached_parts.push((obj, part, attached_part_material));
        attached_parts=attached_parts;
      }

      const response = await fetch("/feedback_materials", {
              method: "POST",
              headers: {"Content-Type": "application/json"},
              body: JSON.stringify({
                "material_name": material_name,
                "object_name":part_parent_name,
                "part_name":part_name,
                "attached_parts":attached_parts,
              }),
      });
      const data = await response.json();
      feedback = await data['response'];
      const role = await data['role'];
    }

    let activeTab='adjust-finish';
    function switchTab(tab) {
      activeTab = tab;
    }

</script>

<div class="card container">
  <div><b>{part_name}</b></div>  
  <DynamicImage bind:this={image} imagepath={material_url} alt={material_name} size={"200px"}/>
  <div id="texture-details">
        <div class="texture-name">Material: {material_name}</div>
        <div class="control">
          <button on:click|preventDefault={suggestSimilarMaterials}>Suggest similar materials </button>
          <button on:click|preventDefault={requestMaterialFeedback}> Request feedback </button>
        </div>
        
        <!-- <div>Material finish: {material_finish}</div> -->
  </div>

  <div class="w3-bar w3-grey tabs">
    <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='adjust-finish'} on:click={()=>switchTab('adjust-finish')} id="adjust-finish-btn">Material Finish</button>
    <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='adjust-texture-map'} on:click={()=>switchTab('adjust-texture-map')} id="adjust-texture-btn">Texture Map</button>
    <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='adjust-color'} on:click={()=>switchTab('adjust-color')} id="adjust-color-btn">Color Finish</button>
    <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='attached-parts'} on:click={()=>switchTab('attached-parts')} id="attached-parts-btn">Attached Parts</button>
    {#if feedback}
      <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='view-feedback'} on:click={()=>switchTab('view-feedback')} id="view-feedback-btn">View Feedback</button>
    {/if}
  </div>

  <div class="card container tab-content" class:active={activeTab==='adjust-finish'}>
    <h5><b>Adjust Finish</b></h5> 
    <div class="control">
      <!-- <span>Is Transparent?: </span> 
      <input type="checkbox" id="transparency" bind:checked={isTransparent} on:change={fook} /> -->
      <span>Opacity: </span>
      <div style="width:100%; align-items:inherit; justify-content:inherit;"> 
        <RangeSlider on:change={updateFinish} bind:values={opacity} min={0} max={1} step={0.1} float={true} pips/> 
      </div>
    </div>
    <div class="control">
      <span>Roughness: </span>
      <div style="width:100%; align-items:inherit; justify-content:inherit;"> 
        <RangeSlider on:change={updateFinish} bind:values={roughness} min={0} max={1} step={0.1} float={true} pips/> 
      </div>
    </div>
    <div class="control">
      <span>Metalness: </span>
      <div style="width:100%; align-items:inherit; justify-content:inherit;"> 
        <RangeSlider on:change={updateFinish} bind:values={metalness} min={0} max={1} step={0.1} float={true} pips/> 
      </div>
    </div>
    
  </div>
  <div class="card container tab-content " class:active={activeTab==='adjust-texture-map'}>
    <h5><b>Adjust Texture Map</b></h5>
    <div class="control">
      <div class="card container" style="height: auto;">
        <h6> <b> Translation </b></h6>
        <div class="control">
          <span>X:</span>
          <NumberSpinner on:change={updateTextureMapOrientation} bind:value={translationX} min=0.0 max=1 step=0.01 decimals=2 precision=0.01/>
        </div>
        <div class="control">
          <span>Y:</span>
          <NumberSpinner on:change={updateTextureMapOrientation} bind:value={translationY} min=0.0 max=1 step=0.01 decimals=1 precision=0.01/>
        </div>
      </div>

      <div class="card container" style="height: auto;">
        <h6> <b> Rotation </b></h6>
        <div class="control">
          <span>Z: </span>
          <NumberSpinner on:change={updateTextureMapOrientation} bind:value={rotation} min=0.0 max=6.28 step=0.01 decimals=1 precision=0.01/>
        </div>
      </div>

      <div class="card container" style="height: auto;">
        <h6> <b> Scale </b></h6>
        <div class="control">
          <span>X & Y: </span>
          <NumberSpinner on:change={updateTextureMapOrientation} bind:value={scale} min=0.0 max=5 step=0.01 decimals=1 precision=0.01/>
        </div>
        <div class="control">
          <span>X: </span>
          <NumberSpinner on:change={updateTextureMapOrientation} bind:value={scaleX} min=0.0 max=5 step=0.01 decimals=1 precision=0.01/>
        </div>
        <div class="control">
          <span>Y: </span>
          <NumberSpinner on:change={updateTextureMapOrientation} bind:value={scaleY} min=0.0 max=5 step=0.01 decimals=1 precision=0.01/>
        </div>
      </div>
    </div>
  </div>

  <div class="card container tab-content" class:active={activeTab==='adjust-color'}>
    <h5> <b> Adjust Color </b></h5>

    <div class="control container" id="color-palette-header">
      <!-- No Colors Swatch Option -->
      <label class="swatch selectable" class:selected={selected_swatch_idx===undefined} style="background-color: {no_color.code};">
          <img src="./logos/cancel-svgrepo-com.svg" alt="">
          <input type=radio bind:group={selected_swatch_idx} name={no_color.name} value={undefined}>
      </label>

      <!-- Color Swatch Options from the Selected Palette -->
      <div class="control" style="position: relative;">
          {#if selected_palette_idx != undefined && palettes.length > 0}
              {#each palettes[selected_palette_idx]['palette'] as swatch, i }
                  <label class="swatch selectable" style="background-color: {swatch};" class:selected={selected_swatch_idx===i}>
                    <input type=radio bind:group={selected_swatch_idx} name={swatch} value={i}>
                  </label>
              {/each}
          {/if}

          {#if isOpen}
          <!-- Dropdown list of color palettes -->
            <div class="dropdown-list" style="position: absolute; top: 30px; left: 35px; z-index=1;">
                <!-- Create a palette for the current material's color. -->
                {#if material_color_palette}
                  <label class="control container palette selectable" class:selected={selected_palette_idx===0}>
                    {#each material_color_palette["palette"] as swatch}
                      <div class="swatch" style="background-color: {swatch};"></div>
                    {/each}
                    <input type=radio bind:group={selected_palette_idx} name={0} value={0}>
                  </label>
                  {#each palettes as p,j}
                    <label class="control container palette selectable" class:selected={selected_palette_idx===j+1}>
                      {#each p["palette"] as swatch}
                        <div class="swatch" style="background-color: {swatch};"></div>
                      {/each}
                      <input type=radio bind:group={selected_palette_idx} name={j+1} value={j+1}>
                    </label>
                  {/each}
                {:else}
                  {#each palettes as p,j}
                    <label class="control container palette selectable" class:selected={selected_palette_idx===j}>
                      {#each p["palette"] as swatch}
                        <div class="swatch" style="background-color: {swatch};"></div>
                      {/each}
                      <input type=radio bind:group={selected_palette_idx} name={j} value={j}>
                    </label>
                  {/each}
                {/if}
                
                
            </div>
          {/if}
      </div>
      <!-- Dropdown Button -->
      <!-- svelte-ignore a11y-click-events-have-key-events -->
      <div style=" width: 25px; height: 25px; align-items: center; justify-content: center; cursor: pointer;" on:click={toggleDropDown}> 
        <img src="./logos/dropdown-svgrepo-com.svg" alt="Select a palette" style="width: 100%; height: 100%;" />
      </div>
    </div>

    <!-- Color swatch -->
    {#if selected_swatch_idx===undefined}

      <div id="current-swatch">
        <pre> No color</pre>
      </div>
    {:else}
      <input id="current-swatch" type="color"  
        bind:value={palettes[selected_palette_idx]['palette'][selected_swatch_idx]}
        on:change={updateColor}
      >
    {/if}
  </div>

  <div class="card container tab-content" class:active={activeTab==='attached-parts'}>
    {#if parents.length > 0}
      <h5> <b> Attached Parts </b></h5>
      {#each parents as p}
        <div class="control container">
          <div class="card">
            <h6> <b> Object: {p[0]}  </b></h6>
            <h6> <b> Part: {p[1]} </b></h6>
          </div>
          <DynamicImage imagepath={current_texture_parts[p[0]][p[1]]["mat_image_texture"]} alt={current_texture_parts[p[0]][p[1]]["mat_name"]} size={"100px"}/>
        </div>
      {/each}
    {:else}
      <p> This component is not attached to anything. </p>
    {/if}

  </div>

  {#if feedback}

    <div class="card container tab-content" class:active={activeTab==='view-feedback'}>
      <h5> <b> Feedback </b></h5>
        <p>{feedback}</p>
    </div>
  {/if}


</div>

<style>



    .container {
      border: 1px solid black;
    }

    .card {
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      align-content:center;
      padding: 5px; 
      gap: 5px;
      width: 100%;
      height: auto;
    }

    .control {
      display:flex; 
      flex-direction: row;
      align-items: center;
      justify-content: center;
      align-content:center;
      padding: 5px;
      gap: 5px;
      width: 100%;
      height: 100%;
    }

    
    #texture-details {
      display: flex;
      flex-direction:column;
      justify-content: center;
      align-content:center;
      align-items: center;
      font-size: 0.8rem;
    }


    .texture-name {
      font-weight: bold;
    }

    .dropdown-list {
      background-color: #fff;
    }

    input[type="radio"] {
        opacity: 0;
        position: fixed;
        width:0; 
    }

    #current-swatch {
      border: 1px solid black; 
      width: calc(6 * 25px + 2 * 2px);
      height: calc(6 * 25px + 2 * 2px);
      padding: 0;
    }

    .swatch {
      width: 25px; 
      height: 25px;
      border: 1px solid black; 
      margin-right: 2px;
    }

    .swatch * {
        width: 100%;
        height: 100%;
        align-items: center;
        justify-content: center;
    }

    .selectable:hover {
      cursor:pointer;
    }

    .palette.selectable:hover {
        background-color: grey;
    }

    .palette.selectable.selected {
        background-color: rgb(86, 165, 255);
    }

    .palette.selectable.selected:hover {
        background-color: rgb(86, 165, 255);
    }

    .swatch.selectable:hover {
      border: 3px solid grey;
    }

    .swatch.selectable.selected {
      border: 3px solid blue;
    } 

    .swatch.selectable.selected:hover {
      border: 3px solid blue;
    } 

    .tabs   {
      display:flex; 
      flex-direction: row;
      width: 100%;
      height: 100%;
      align-items: center;
      justify-content: center;
      align-content:center;
      gap: 0px;
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
      /* height: 100%;
      width:100%;
      padding: 5px;
      gap: 5px; */
    }


  </style>
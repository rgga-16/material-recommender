<script>
    import DynamicImage from "./DynamicImage.svelte";
    import NumberSpinner from "svelte-number-spinner";
    import { Circle } from 'svelte-loading-spinners';
    import RangeSlider from "svelte-range-slider-pips";
    import {onMount} from 'svelte';
    import SvelteMarkdown from 'svelte-markdown';

    import {selected_objs_and_parts} from '../stores.js';
    import {saved_color_palettes} from "../stores.js";
    import {chatbot_input_message} from "../stores.js";
    import {actions_panel_tab} from '../stores.js';
    import {generate_tab_page} from '../stores.js';
    import {generate_module} from '../stores.js';
    import {design_brief} from '../stores.js';
    import {use_chatgpt} from '../stores.js';
    import {get} from 'svelte/store';

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

    let use_design_brief = false;

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

    let is_loading_feedback=false;
    
    export let index;
    let material;
    let opacity=[0.5];
    let roughness=[0.5]
    let metalness=[0.5];
    let normalScale=[0];
    let displacementScale=[0];
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
    // console.log(parents);


    
    function adjustMap(map) {
      map.offset.x = translationX;
      map.offset.y = translationY;
      map.rotation = rotation;
      map.repeat.x = scaleX;
      map.repeat.y = scaleY;
    }

    function updateNormalScale() {
      selected_objs_and_parts.update(value => {
        value[index].model.children[0].material.normalScale.x = normalScale[0];
        value[index].model.children[0].material.normalScale.y = normalScale[0];
        return value;
      });
    }

    function updateDisplacementScale() {
      selected_objs_and_parts.update(value => {
        value[index].model.children[0].material.displacementScale = displacementScale[0];
        return value;
      });
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

    function addNewColorPalete() {
      palettes.push({
        name: 'New Palette',
        palette: [
          "#FFFFFF",
          "#FFFFFF",
          "#FFFFFF",
          "#FFFFFF",
          "#FFFFFF",
        ]
      });
      palettes=palettes;
      saved_color_palettes.set(palettes);
      
    }

    function updateColor() {
      let color = palettes[selected_palette_idx]['palette'][selected_swatch_idx];
      // console.log(selected_palette_idx);
      console.log(color);
      const hexNumber = parseInt(color.substring(1), 16);
      // console.log(hexNumber);

      selected_objs_and_parts.update(value => {
        value[index].model.children[0].material.color.setHex(hexNumber);
        value[index].model.children[0].material.color_hex = hexNumber;
        return value;
      });

      current_texture_parts[part_parent_name][part_name]['mat_color'] = hexNumber;
      curr_texture_parts.set(current_texture_parts);
    }

    function suggestSimilarMaterials() {
      if(part_parent_name===part_name){
        let query = "Can you suggest similar materials to " + material_name + "for a " + part_parent_name + "?";
        actions_panel_tab.set("chatbot");
        chatbot_input_message.set(query);
      } else {
        let query = "Can you suggest similar materials to " + material_name + " for a " + part_parent_name + " " + part_name + "?";
        actions_panel_tab.set("chatbot");
        chatbot_input_message.set(query);
      }
    }

    let feedback =undefined;
    let formatted_feedback = undefined;
    let intro_text=undefined;
    let references=undefined; 
    let activeAspect;
    async function requestMaterialFeedback() {
      const start = performance.now();
      feedback=undefined;
      formatted_feedback=undefined; intro_text=undefined; references=undefined;
      switchTab("view-feedback");

      let context=null; 
      if(use_design_brief) {
        context = get(design_brief);
      }

      let attached_parts = [];
      for (const p in parents) {
        const parent = parents[p]; const obj = parent[0]; const part = parent[1];
        const attached_part_material = current_texture_parts[obj][part]['mat_name'];
        attached_parts.push([obj, part, attached_part_material]); attached_parts=attached_parts;
      }

      is_loading_feedback=true;
      const response = await fetch("/feedback_materials", {
              method: "POST",
              headers: {"Content-Type": "application/json"},
              body: JSON.stringify({
                "material_name": material_name,
                "object_name":part_parent_name,
                "part_name":part_name,
                "attached_parts":attached_parts,
                "design_brief":context
              }),
      });

      const data = await response.json();
      
      const unformatted_feedback = await data['unformatted_response'];
      const role = await data['role'];
      intro_text = await data['intro_text'];
      formatted_feedback = await data['formatted_response'];
      references = await data['references'];

      activeAspect= await Object.keys(formatted_feedback)[0];

      is_loading_feedback=false;

      feedback = unformatted_feedback;

      current_texture_parts[part_parent_name][part_name]['feedback'] = {};
      current_texture_parts[part_parent_name][part_name]['feedback']['formatted_feedback'] = formatted_feedback;
      current_texture_parts[part_parent_name][part_name]['feedback']['intro_text'] = intro_text;
      current_texture_parts[part_parent_name][part_name]['feedback']['references'] = references;
      curr_texture_parts.set(current_texture_parts);

      const end = performance.now();
      console.log("Requesting material feedback took " + (end - start) + " milliseconds.");
    }

    let activeTab='adjust-finish';
    function switchTab(tab) {
      activeTab = tab;
    }
    let gen_module;
    onMount(async () => {
      material = sel_objs_and_parts[index].model.children[0].material;
      opacity = [material.opacity];
      roughness = [material.roughness]; 
      metalness = [material.metalness];
      displacementScale = [material.displacementScale];
      normalScale = [material.normalScale.x];
      isTransparent = material.transparent;

      translationX = material.map.offset.x;
      translationY = material.map.offset.y;
      rotation = material.map.rotation;
      scaleX = material.map.repeat.x;
      scaleY = material.map.repeat.y;

      if(current_texture_parts[part_parent_name][part_name]['feedback']) {
        formatted_feedback = current_texture_parts[part_parent_name][part_name]['feedback']['formatted_feedback'];
        intro_text = current_texture_parts[part_parent_name][part_name]['feedback']['intro_text'];
        references = current_texture_parts[part_parent_name][part_name]['feedback']['references'];
        activeAspect= Object.keys(formatted_feedback)[0];
      }
      console.log(parents);
      gen_module = get(generate_module);
    });

    function applyFinishSuggestion(finish_suggestion) {
      switchTab('adjust-finish');
      opacity = [finish_suggestion["opacity"]];
      roughness = [finish_suggestion["roughness"]];
      metalness = [finish_suggestion["metalllic"]];
      updateFinish();
    }

    function generate(material_name) {
      actions_panel_tab.set("generate");
      generate_tab_page.set(0);
      gen_module.generate_textures(material_name);
    }
</script>

<div class="card container">
  <div class="control"> <b>{part_parent_name}</b> | <b>{part_name}</b> </div>
  <DynamicImage bind:this={image} imagepath={material_url} alt={material_name} size={"200px"}/>
  <div id="texture-details">
        <div class="texture-name">Material: {material_name}</div>
        {#if current_texture_parts[part_parent_name][part_name]['mat_color']}
          <div class="texture-name">Color: {current_texture_parts[part_parent_name][part_name]['mat_color']}</div>
        {:else}
          <div class="texture-name">Color: None</div>
        {/if}
        {#if current_texture_parts[part_parent_name][part_name]['mat_finish']}
          <div class="texture-name">Finish: {current_texture_parts[part_parent_name][part_name]['mat_finish']}</div>
        {:else}
        <div class="texture-name">Finish: None</div>
        {/if}
        {#if get(use_chatgpt)}
          <div class="control">
            <button on:click|preventDefault={suggestSimilarMaterials}>Suggest similar materials </button>
            <button on:click|preventDefault={requestMaterialFeedback}> Request feedback </button>
            <label>
              <input type="checkbox" bind:checked={use_design_brief} >
              Based on design brief
            </label>
          </div>
        {/if}
  </div>

  <div class="w3-bar w3-grey tabs">
    <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='adjust-finish'} on:click={()=>switchTab('adjust-finish')} id="adjust-finish-btn">Material Finish</button>
    <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='adjust-texture-map'} on:click={()=>switchTab('adjust-texture-map')} id="adjust-texture-btn">Texture Map</button>
    <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='adjust-color'} on:click={()=>switchTab('adjust-color')} id="adjust-color-btn">Color Finish</button>
    <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='attached-parts'} on:click={()=>switchTab('attached-parts')} id="attached-parts-btn">Attached Parts</button>
    {#if get(use_chatgpt)}
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
<!-- WIP
    <div class="control">
      <span>Normal Map Strength: </span>
      <div style="width:100%; align-items:inherit; justify-content:inherit;"> 
        <RangeSlider on:change={updateNormalScale} bind:values={normalScale} min={0} max={10} step={0.1} float={true} pips/> 
      </div>
    </div>

    <div class="control">
      <span>Height Map Strength: </span>
      <div style="width:100%; align-items:inherit; justify-content:inherit;"> 
        <RangeSlider on:change={updateDisplacementScale} bind:values={displacementScale} min={0} max={10} step={0.1} float={true} pips/> 
      </div>
    </div> -->
  </div>

  <div class="card container tab-content " class:active={activeTab==='adjust-texture-map'}>
    <h5><b>Adjust Texture Map</b></h5>
    <div class="control">
      <div class="card container" style="height: auto;">
        <h6> <b> Translation </b></h6>
        <div class="control">
          <span>X:</span>
          <NumberSpinner on:change={updateTextureMapOrientation} bind:value={translationX} min=0.0 max=10 step=0.01 decimals=2 precision=0.01/>
        </div>
        <div class="control">
          <span>Y:</span>
          <NumberSpinner on:change={updateTextureMapOrientation} bind:value={translationY} min=0.0 max=10 step=0.01 decimals=1 precision=0.01/>
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
          <NumberSpinner on:change={updateTextureMapOrientation} bind:value={scale} min=0.0 max=20 step=0.01 decimals=1 precision=0.01/>
        </div>
        <div class="control">
          <span>X: </span>
          <NumberSpinner on:change={updateTextureMapOrientation} bind:value={scaleX} min=0.0 max=20 step=0.01 decimals=1 precision=0.01/>
        </div>
        <div class="control">
          <span>Y: </span>
          <NumberSpinner on:change={updateTextureMapOrientation} bind:value={scaleY} min=0.0 max=20 step=0.01 decimals=1 precision=0.01/>
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
                    <input type=radio bind:group={selected_swatch_idx} name={swatch} value={i} on:change={() => updateColor()}>
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
                  <button on:click|preventDefault={() => addNewColorPalete()}> Add new </button>
                {:else}
                  {#each palettes as p,j}
                    <label class="control container palette selectable" class:selected={selected_palette_idx===j}>
                      {#each p["palette"] as swatch}
                        <div class="swatch" style="background-color: {swatch};"></div>
                      {/each}
                      <input type=radio bind:group={selected_palette_idx} name={j} value={j}>
                    </label>
                  {/each}
                  <button on:click|preventDefault={() => addNewColorPalete()}> Add new </button>
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
        on:change={() => updateColor()}
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

  {#if get(use_chatgpt)}
    <div class="card container tab-content" class:active={activeTab==='view-feedback'} style="flex-wrap:wrap;">
      <h5> <b> Feedback </b></h5>
        {#if formatted_feedback}
          <SvelteMarkdown source={intro_text} />
          <div class="w3-bar w3-grey tabs">
            {#each Object.keys(formatted_feedback) as aspect}
              <button class="w3-bar-item w3-button tab-btn" class:active={activeAspect===aspect} on:click={() => {activeAspect = aspect;}}>
                {aspect}
              </button>
            {/each}
          </div>

          {#each Object.keys(formatted_feedback) as aspect}
            <div class="card container tab-content" class:active={activeAspect===aspect}>
              <SvelteMarkdown source={formatted_feedback[aspect]['feedback']} />
              
              <div class="card container">
                <h6> <b> <u> Suggestions </u>  </b></h6>
                <div class="control" style="justify-content:space-between;">
                  {#if formatted_feedback[aspect]['suggestions'].length <= 0}
                    <p> No suggestions provided. </p>
                  {:else}
                    {#each formatted_feedback[aspect]['suggestions'] as suggestion}
                      <div class="card container" style="height:100%;">
                        {#if suggestion[1] === "material" && suggestion.length===3} 
                          <span> <b> {suggestion[0]} </b></span>
                          <DynamicImage imagepath={suggestion[2]} alt={suggestion[0]} size={"100px"} is_draggable={true}/>
                          <span> <b> {suggestion[1].charAt(0).toUpperCase() + suggestion[1].slice(1)} </b></span>

                          <button  on:click={() => {generate(suggestion[0])}}> 
                            Generate more! 
                            <img src="./logos/magic-wand-svgrepo-com.svg" style="width:25px; height:25px; align-items: center; justify-content: center;" alt="Generate">
                          </button>
                        {:else if suggestion[1] === "attachment" && suggestion.length===3}
                          <span> <b> {suggestion[0]} </b></span>
                          <DynamicImage imagepath={suggestion[2]} alt={suggestion[0]} size={"100px"}/>
                          <span><b> {suggestion[1].charAt(0).toUpperCase() + suggestion[1].slice(1)} </b></span>
                        {:else if suggestion[1] === "finish" && suggestion.length===3}
                          <span> <b> {suggestion[0]} </b></span>
                          <div class="card container">
                            <span> Opacity: {suggestion[2]["opacity"]}</span>
                            <span> Roughness: {suggestion[2]["roughness"]}</span>
                            <span> Metalness: {suggestion[2]["metallic"]}</span>
                          </div>
                          <span><b> {suggestion[1].charAt(0).toUpperCase() + suggestion[1].slice(1)} </b></span>
                          <button  on:click={() => {applyFinishSuggestion(suggestion[2])}}> Apply Finish </button>
                        {:else}
                          <span> <b> {suggestion[0]} </b></span>
                          <span><b> {suggestion[1].charAt(0).toUpperCase() + suggestion[1].slice(1)} </b></span>
                        {/if} 
                      </div>
                    {/each}
                  {/if}

                  
                </div>
              </div>
            </div>
          {/each}
          
          <h6> <b> <u> References </u>  </b></h6>
          <SvelteMarkdown source={references} />
        {:else if is_loading_feedback}
          <div class="images-placeholder">
            Requesting feedback...
            <Circle size="60" color="#FF3E00" unit="px" duration="1s" />
          </div>
        {:else}
          <p> No feedback yet. </p>
        {/if}
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

    .images-placeholder {
        width: 100%;
        height: 100%;
        border: 1px dashed black;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
    }


  </style>
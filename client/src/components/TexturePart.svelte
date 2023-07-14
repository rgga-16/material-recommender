<svelte:options accessors={true}/>
<script>
    import DynamicImage from "./DynamicImage.svelte";
    import NumberSpinner from "svelte-number-spinner";
    import { Circle } from 'svelte-loading-spinners';
    import RangeSlider from "svelte-range-slider-pips";
    import {onMount} from 'svelte';
    import SvelteMarkdown from 'svelte-markdown';

    import EditableTextbox from "./EditableTextbox.svelte";

    import {in_japanese, selected_objs_and_parts} from '../stores.js';
    import {translate,addToHistory} from '../main.js';
    import {saved_color_palettes} from "../stores.js";
    import {chatbot_input_message} from "../stores.js";
    import {actions_panel_tab} from '../stores.js';
    import {generate_tab_page} from '../stores.js';
    import {generate_module} from '../stores.js';
    import {design_brief} from '../stores.js';
    import {use_chatgpt} from '../stores.js';
    import {get} from 'svelte/store';

    import {curr_texture_parts, objects_3d, information_panel_global} from '../stores.js';

    let image;
    export function updateImage() {
      image.getImage();
    }
    
    let isMouseDown=false;

    let information_panel;
    information_panel_global.subscribe(value => {
      information_panel = value;
    });

    let japanese;
    in_japanese.subscribe(value => {
      japanese = value;
    });

    let current_texture_parts;
    curr_texture_parts.subscribe(value => {
      current_texture_parts = value;
      if(image) {
        image.getImage();
      }
    });

    let all_3d_objects;
    objects_3d.subscribe(value => {
      all_3d_objects = value;
    });
    
    export let index;
    export let part_parent_name;
    export let part_name;
    export let material_name; 
    export let material_url;
    export let material_finish; 
    export let material_color=null; //Color code of the material
    /**
     * parents = [
     *  (object, part)
     * 
     * ]
     */
     export let parents = []; //List of parts that this part is attached to.

    let use_design_brief = false;

    
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
    });

    let selected_swatch_idx = undefined;
    const no_color = {name: 'No Color', code: '#FFFFFF'}

    let isOpen=false;
    function toggleDropDown() {
        isOpen = !isOpen;
    }

    
    export function updateNormalScale(normalScale) {
      selected_objs_and_parts.update(value => {
        value[index].model.children[0].material.normalScale.x = normalScale;
        value[index].model.children[0].material.normalScale.y = normalScale;
        return value;
      });
    }

    export function updateDisplacementScale(displacementScale) {
      selected_objs_and_parts.update(value => {
        value[index].model.children[0].material.displacementScale = displacementScale;
        return value;
      });
    }

    export function changeProperty(property, new_value, old_value=0) {
      if(current_texture_parts[part_parent_name][part_name][property]) {
        old_value = current_texture_parts[part_parent_name][part_name][property];
      }
      curr_texture_parts.update(value => {
        value[part_parent_name][part_name][property] = new_value;
        return value;
      });
      addToHistory("Change " + property, 
        part_parent_name, part_name, 
        [property], 
        [old_value], 
        [new_value]
      );
    }


    export function updateOpacity(opacity_val) {
      selected_objs_and_parts.update(value => {
        value[index].model.children[0].material.transparent= true;
        value[index].model.children[0].material.opacity = opacity_val;
        return value;
      });
    }

    export function updateMetalness(metalness_val) {
      selected_objs_and_parts.update(value => {
        value[index].model.children[0].material.metalness = metalness_val;
        return value;
      });
    }

    export function updateRoughness(roughness_val) {
      selected_objs_and_parts.update(value => {
        value[index].model.children[0].material.roughness = roughness_val;
        return value;
      });
    }

    function radianToDegree(radians) {
      return radians * (180/Math.PI);
    }

    function degreeToRadians(degrees) {
      return degrees * (Math.PI/180);
    }

    

    function setScale(map, x_or_y, value) {
      map.repeat[x_or_y] = value;
    }

    function setOffset(map,x_or_y, value) {
      map.offset[x_or_y] = value;
    }


    export function updateTextureMapOffset(x_or_y,val) {
      selected_objs_and_parts.update(value => {
        setOffset(value[index].model.children[0].material.map, x_or_y,val);

        if (value[index].model.children[0].material.normalMap) {
          setOffset(value[index].model.children[0].material.normalMap, x_or_y,val);
        }
        if (value[index].model.children[0].material.aoMap) {
          setOffset(value[index].model.children[0].material.aoMap, x_or_y,val);
        }
        if (value[index].model.children[0].material.alphaMap) {
          setOffset(value[index].model.children[0].material.alphaMap, x_or_y,val);
        }
        if(value[index].model.children[0].material.emissiveMap) {
          setOffset(value[index].model.children[0].material.emissiveMap, x_or_y,val);
        }
        if (value[index].model.children[0].material.lightMap) {
          setOffset(value[index].model.children[0].material.lightMap, x_or_y,val);
        }
        if(value[index].model.children[0].material.metalnessMap) {
          setOffset(value[index].model.children[0].material.metalnessMap, x_or_y,val);
        }
        if(value[index].model.children[0].material.roughnessMap) {
          setOffset(value[index].model.children[0].material.roughnessMap, x_or_y,val);
        }
        if(value[index].model.children[0].material.displacementMap) {
          setOffset(value[index].model.children[0].material.displacementMap, x_or_y,val);
        }
        if(value[index].model.children[0].material.bumpMap) {
          setOffset(value[index].model.children[0].material.bumpMap, x_or_y,val);
        }
        if(value[index].model.children[0].material.envMap) {
          setOffset(value[index].model.children[0].material.envMap, x_or_y,val);
        }
        return value;
      });
    }

    export function updateTextureMapScale(x_or_y,val) {
      selected_objs_and_parts.update(value => {
        setScale(value[index].model.children[0].material.map, x_or_y, val);
        if (value[index].model.children[0].material.normalMap) {
          setScale(value[index].model.children[0].material.normalMap, x_or_y, val);
        }
        if (value[index].model.children[0].material.aoMap) {
          setScale(value[index].model.children[0].material.aoMap, x_or_y, val);
        }
        if (value[index].model.children[0].material.alphaMap) {
          setScale(value[index].model.children[0].material.alphaMap, x_or_y, val);
        }
        if(value[index].model.children[0].material.emissiveMap) {
          setScale(value[index].model.children[0].material.emissiveMap, x_or_y, val);
        }
        if (value[index].model.children[0].material.lightMap) {
          setScale(value[index].model.children[0].material.lightMap, x_or_y, val);
        }
        if(value[index].model.children[0].material.metalnessMap) {
          setScale(value[index].model.children[0].material.metalnessMap, x_or_y, val);
        }
        if(value[index].model.children[0].material.roughnessMap) {
          setScale(value[index].model.children[0].material.roughnessMap, x_or_y, val);
        }
        if(value[index].model.children[0].material.displacementMap) {
          setScale(value[index].model.children[0].material.displacementMap, x_or_y, val);
        }
        if(value[index].model.children[0].material.bumpMap) {
          setScale(value[index].model.children[0].material.bumpMap, x_or_y, val);
        }
        if(value[index].model.children[0].material.envMap) {
          setScale(value[index].model.children[0].material.envMap, x_or_y, val);
        }
        return value;
      });
    }

    function setOrientation(map,rot) {
      map.rotation = degreeToRadians(rot);
    }

    export function updateTextureMapOrientation(rot) {
      selected_objs_and_parts.update(value => {
        setOrientation(value[index].model.children[0].material.map,rot);
        if (value[index].model.children[0].material.normalMap) {
          setOrientation(value[index].model.children[0].material.normalMap,rot);
        }
        if (value[index].model.children[0].material.aoMap) {
          setOrientation(value[index].model.children[0].material.aoMap,rot);
        }
        if (value[index].model.children[0].material.alphaMap) {
          setOrientation(value[index].model.children[0].material.alphaMap,rot);
        }
        if(value[index].model.children[0].material.emissiveMap) {
          setOrientation(value[index].model.children[0].material.emissiveMap,rot);
        }
        if (value[index].model.children[0].material.lightMap) {
          setOrientation(value[index].model.children[0].material.lightMap,rot);
        }
        if(value[index].model.children[0].material.metalnessMap) {
          setOrientation(value[index].model.children[0].material.metalnessMap,rot);
        }
        if (value[index].model.children[0].material.bumpMap) {
          setOrientation(value[index].model.children[0].material.bumpMap,rot);
        }
        if(value[index].model.children[0].material.displacementMap) {
          setOrientation(value[index].model.children[0].material.displacementMap,rot);
        }
        if(value[index].model.children[0].material.envMap) {
          setOrientation(value[index].model.children[0].material.envMap,rot);
        }
        if(value[index].model.children[0].material.normalMap) {
          setOrientation(value[index].model.children[0].material.normalMap,rot);
        }
        if (value[index].model.children[0].material.roughnessMap) {
          setOrientation(value[index].model.children[0].material.roughnessMap,rot);
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

      current_texture_parts[part_parent_name][part_name]['color'] = hexNumber;
      curr_texture_parts.set(current_texture_parts);

      selected_objs_and_parts.update(value => {
        value[index].model.children[0].material.color.setHex(hexNumber);
        value[index].model.children[0].material.color_hex = hexNumber;
        return value;
      });

      
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
    let japanese_formatted_feedback = undefined;


    let intro_text=undefined;
    let references=undefined; 
    let activeAspect;
    async function requestMaterialFeedback() {
      const start = performance.now();
      feedback=undefined;
      formatted_feedback=undefined; intro_text=undefined; references=undefined; japanese_formatted_feedback=undefined;
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


      japanese_formatted_feedback={...formatted_feedback}; 
      if(japanese) {
        for (let aspect in japanese_formatted_feedback) {
          japanese_formatted_feedback[aspect]['feedback'] = await translate("EN","JA",japanese_formatted_feedback[aspect]['feedback']);

          for (let i=0; i < japanese_formatted_feedback[aspect]['suggestions'].length; i++) {
            let suggestion = japanese_formatted_feedback[aspect]['suggestions'][i][0];
            japanese_formatted_feedback[aspect]['suggestions'][i][0] = await translate("EN","JA",suggestion);
          }
        }
      }


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
      rotation = radianToDegree(material.map.rotation);
      scaleX = material.map.repeat.x;
      scaleY = material.map.repeat.y;

      if(current_texture_parts[part_parent_name][part_name]['feedback']) {
        formatted_feedback = current_texture_parts[part_parent_name][part_name]['feedback']['formatted_feedback'];
        intro_text = current_texture_parts[part_parent_name][part_name]['feedback']['intro_text'];
        references = current_texture_parts[part_parent_name][part_name]['feedback']['references'];
        activeAspect= Object.keys(formatted_feedback)[0];
      }

      if(current_texture_parts[part_parent_name][part_name]['opacity']) {
        opacity = [current_texture_parts[part_parent_name][part_name]['opacity']];
      }
      if(current_texture_parts[part_parent_name][part_name]['mat_metalness']) {
        metalness = [current_texture_parts[part_parent_name][part_name]['mat_metalness']];
      }
      if(current_texture_parts[part_parent_name][part_name]['roughness']) {
        roughness = [current_texture_parts[part_parent_name][part_name]['roughness']];
      }
      if(current_texture_parts[part_parent_name][part_name]['color']) {
        material_color = current_texture_parts[part_parent_name][part_name]['color'];
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
        palettes.unshift(material_color_palette);
        palettes=palettes;
        selected_palette_idx=0;
        selected_swatch_idx=0;
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
    let none = "none";
</script>

<div class="card container">
  <div class="control"> 
    {#if part_parent_name===part_name} 
    <b>{part_name}</b> 
    {:else}
      <b>{part_parent_name}</b> | <b>{part_name}</b> 
    {/if}
    
  </div>
  <DynamicImage bind:this={image} bind:imagepath={material_url} alt={material_name} size={"200px"}/>
  <div id="texture-details">
        <div class="texture-name control">
          {japanese ? "素材：" : "Material:"} <EditableTextbox bind:text={current_texture_parts[part_parent_name][part_name]['mat_name']} />
        </div>
        {#if current_texture_parts[part_parent_name][part_name]['color']}
          <div class="texture-name control">
            {japanese ? "カラー：": "Color:"}<input type="text" readonly="readonly" bind:value={current_texture_parts[part_parent_name][part_name]['color']}>
          </div>
        {:else}
          <div class="texture-name control">
            {japanese ? "カラー：": "Color:"} <input type="text" readonly="readonly" value={"none"}>
          </div>
        {/if}
        {#if current_texture_parts[part_parent_name][part_name]['mat_finish']}
          <div class="texture-name control">
            {japanese ? "素材仕上げ：": "Finish:"} <EditableTextbox bind:text={current_texture_parts[part_parent_name][part_name]['mat_finish']} />
          </div>
        {:else}
          <div class="texture-name control">
            {japanese ? "素材仕上げ：": "Finish:"} <EditableTextbox bind:text={none} />
          </div>
        {/if}
        {#if get(use_chatgpt)}
          <div class="control">
            <button on:click|preventDefault={suggestSimilarMaterials}>{japanese ? "類似素材の提案" : "Suggest similar materials"} </button>
            <div style="border:1px black;">
              <button on:click|preventDefault={requestMaterialFeedback}> {japanese ? "フィードバックのリクエスト": "Request feedback"}  </button>
              <label>
                <input type="checkbox" bind:checked={use_design_brief} >
                {japanese ? "デザイン・ブリーフに基づく" : "Based on design brief"}
              </label>
            </div>
            
          </div>
        {/if}
  </div>

  <div class="w3-bar w3-grey tabs">
    <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='adjust-finish'} on:click={()=>switchTab('adjust-finish')} id="adjust-finish-btn"> {japanese ? "素材仕上げ" : "Material Finish"} </button>
    <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='adjust-texture-map'} on:click={()=>switchTab('adjust-texture-map')} id="adjust-texture-btn"> {japanese ? "テクスチャマップ": "Texture Map"}</button>
    <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='adjust-color'} on:click={()=>switchTab('adjust-color')} id="adjust-color-btn"> {japanese ? "カラー仕上げ" : "Color Finish"}</button>
    <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='attached-parts'} on:click={()=>switchTab('attached-parts')} id="attached-parts-btn"> {japanese ? "付属部品" : "Attached Parts"}</button>
    {#if get(use_chatgpt)}
      <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='view-feedback'} on:click={()=>switchTab('view-feedback')} id="view-feedback-btn"> {japanese ? "フィードバックを見る" : "View Feedback"} </button>
    {/if}
  </div>

  <div class="card container tab-content" class:active={activeTab==='adjust-finish'}>
    <h5><b> {japanese ? "素材仕上げの調整" : "Adjust Material Finish"}</b></h5> 
    <div class="control">
      <span> {japanese ? "不透明度：" : "Opacity:"}   </span>
      <div style="width:100%; align-items:inherit; justify-content:inherit;" on:mousedown={() => isMouseDown=true} on:mouseup = {() => {isMouseDown=false;changeProperty("opacity", opacity[0], 1.0)}}> 
        <RangeSlider on:change={() => updateOpacity(opacity[0])} bind:values={opacity} min={0} max={1} step={0.1} float={true} pips /> 
      </div>
    </div>
    <div class="control">
      <span> {japanese ? "粗さ：" : "Roughness:"} </span>
      <div style="width:100%; align-items:inherit; justify-content:inherit;" on:mousedown={() => isMouseDown=true} on:mouseup = {() => {isMouseDown=false;changeProperty("roughness", roughness[0], 0.5)}}> 
        <RangeSlider on:change={() => updateRoughness(roughness[0])} bind:values={roughness} min={0} max={1} step={0.1} float={true} pips/> 
      </div>
    </div>
    <div class="control">
      <span> {japanese ? "金属的だ：": "Metalness:"} </span>
      <div style="width:100%; align-items:inherit; justify-content:inherit;" on:mousedown={() => isMouseDown=true} on:mouseup = {() => {isMouseDown=false;changeProperty("metalness", metalness[0], 0.5)}}> 
        <RangeSlider on:change={() => updateMetalness(metalness[0])} bind:values={metalness} min={0} max={1} step={0.1} float={true} pips/> 
      </div>
    </div>
    <div class="control">
      <span> {japanese ? "法線マップの強度:" : "Normal Scale:"} </span>
      <div style="width:100%; align-items:inherit; justify-content:inherit;" on:mousedown={() => isMouseDown=true} on:mouseup = {() => {isMouseDown=false;changeProperty("normalScale", normalScale[0], 0.5)}}> 
        <RangeSlider on:change={() => updateNormalScale(normalScale[0])} bind:values={normalScale} min={0} max={10} step={0.1} float={true}/> 
      </div>
    </div>
    <div class="control">
      <span> {japanese ? "高さマップの強度:" : "Height Scale:"} </span>
      <div style="width:100%; align-items:inherit; justify-content:inherit;" on:mousedown={() => isMouseDown=true} on:mouseup = {() => {isMouseDown=false;changeProperty("displacementScale", displacementScale[0], 0.00)}}> 
        <RangeSlider on:change={() => updateDisplacementScale(displacementScale[0])} bind:values={displacementScale} min={0} max={0.5} step={0.01} float={true}/> 
      </div>
    </div>
  </div>

  <div class="card container tab-content " class:active={activeTab==='adjust-texture-map'}>
    <h5><b> {japanese ? "テクスチャマップを調整する": "Adjust Texture Map"} </b></h5>
    <div class="control">

      <div class="card container" style="height: auto;">
        <h6> <b> {japanese ? "平行移動": "Translation"} </b></h6>
        <div class="control" on:mousedown={() => isMouseDown=true} on:mouseup = {() => {isMouseDown=false;changeProperty("offsetX", translationX, 0.0)}}>
          <span>X:</span>
          <NumberSpinner on:change={() => updateTextureMapOffset("x",translationX)} bind:value={translationX} min=0.0 max=20 step=0.01 decimals=1 precision=0.01/>
        </div>
        <div class="control" on:mousedown={() => isMouseDown=true} on:mouseup = {() => {isMouseDown=false;changeProperty("offsetY", translationY, 0.0)}}>
          <span>Y:</span>
          <NumberSpinner on:change={() => updateTextureMapOffset("y",translationY)} bind:value={translationY} min=0.0 max=20 step=0.01 decimals=1 precision=0.01/>
        </div>
      </div>

      <div class="card container" style="height: auto;">
        <h6> <b> {japanese ? "回転": "Rotation"} </b></h6>
        <div class="control" on:mousedown={() => isMouseDown=true} on:mouseup = {() => {isMouseDown=false; changeProperty("rotation",rotation,0)}}>
          <span>Z: </span>
          <NumberSpinner on:change={() =>  updateTextureMapOrientation(rotation)} bind:value={rotation} min=0 max=360 step=0.1 decimals=1 precision=0.1/>°
        </div>
      </div>

      <div class="card container" style="height: auto;">
        <h6> <b> {japanese ? "スケール": "Scale"}  </b></h6>
        <div class="control" on:mousedown={() => isMouseDown=true} on:mouseup = {() => {isMouseDown=false; changeProperty("scaleX",scale,0); changeProperty("scaleY",scale,1)}}>
          <span>X & Y: </span>
          <NumberSpinner on:change={() => {updateTextureMapScale("x",scale);updateTextureMapScale("y",scale)}} bind:value={scale} min=1.0 max=40 step=0.01 decimals=1 precision=0.01/>
        </div>
        <div class="control" on:mousedown={() => isMouseDown=true} on:mouseup = {() => {isMouseDown=false; changeProperty("scaleX",scaleX,1)}}>
          <span>X: </span>
          <NumberSpinner on:change={() => updateTextureMapScale("x",scaleX)} bind:value={scaleX} min=1.0 max=40 step=0.01 decimals=1 precision=0.01/>
        </div>
        <div class="control" on:mousedown={() => isMouseDown=true} on:mouseup = {() => {isMouseDown=false; changeProperty("scaleY",scaleY,1)}}>
          <span>Y: </span>
          <NumberSpinner on:change={() => updateTextureMapScale("y",scaleY)} bind:value={scaleY} min=1.0 max=40 step=0.01 decimals=1 precision=0.01/>
        </div>
      </div>
    </div>
  </div>

  <div class="card container tab-content" class:active={activeTab==='adjust-color'}>
    <h5> <b> {japanese ? "カラー仕上げの調整": "Adjust Color Finish"}  </b></h5>

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
            <div class="dropdown-list" style="position: absolute; top: 30px; left: 170px; z-index=1;">
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
                  <button on:click|preventDefault={() => addNewColorPalete()}> 
                    {japanese ? "新規追加" : "Add new"} 
                    <img src="./logos/add-svgrepo-com.svg" style="width:25px; height:25px; align-items: center; justify-content: center;" alt="Add new color palette">
                  </button>
                {:else}
                  {#each palettes as p,j}
                    <label class="control container palette selectable" class:selected={selected_palette_idx===j}>
                      {#each p["palette"] as swatch}
                        <div class="swatch" style="background-color: {swatch};"></div>
                      {/each}
                      <input type=radio bind:group={selected_palette_idx} name={j} value={j}>
                    </label>
                  {/each}
                  <button on:click|preventDefault={() => addNewColorPalete()}> 
                    {japanese ? "新規追加" : "Add new"} 
                    <img src="./logos/add-svgrepo-com.svg" style="width:25px; height:25px; align-items: center; justify-content: center;" alt="Add new color palette">
                  </button>
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
        <pre> {japanese ? "色なし": "No color"}  </pre>
      </div>
    {:else}
      <input id="current-swatch" type="color"  
        bind:value={palettes[selected_palette_idx]['palette'][selected_swatch_idx]}
        on:change={() => updateColor()}
        on:mousedown={() => isMouseDown=true} 
        on:mouseup = {() => isMouseDown=false}
      >
    {/if}
  </div>

  <div class="card container tab-content" class:active={activeTab==='attached-parts'}>
    {#if parents.length > 0}
      <h5> <b> {japanese ? "付属部品" : "Attached Parts"} </b></h5>
      {#each parents as p}
        <div class="control container">
          <div class="card">
            <h6> <b> {japanese ? "オブジェクト：" : "Object:"}  {p[0]}  </b></h6>
            <h6> <b> {japanese ? "パート" : "Part:"}  {p[1]} </b></h6>
          </div>
          <DynamicImage imagepath={current_texture_parts[p[0]][p[1]]["mat_image_texture"]} alt={current_texture_parts[p[0]][p[1]]["mat_name"]} size={"100px"}/>
        </div>
      {/each}
    {:else}
      <p> {japanese ? "このコンポーネントは何にも取り付けられていない。" : "This component is not attached to anything."}  </p>
    {/if}
  </div>

  {#if get(use_chatgpt)}
    <div class="card container tab-content" class:active={activeTab==='view-feedback'} style="flex-wrap:wrap;">
      <h5> <b> {japanese ?  "フィードバック" : "Feedback"}</b></h5>
        {#if formatted_feedback && japanese_formatted_feedback}
          <SvelteMarkdown source={intro_text} />
          <div class="w3-bar w3-grey tabs">
            {#each Object.keys(formatted_feedback) as aspect}
              <button class="w3-bar-item w3-button tab-btn" class:active={activeAspect===aspect} on:click={() => {activeAspect = aspect;}}>
                {#if in_japanese}
                  {aspect==="assembly" ? "組み立て" : aspect==="availability" ? "素材の入手性" : aspect==="cost" ? "コスト" : aspect==="durability" ? "素材の耐久性" : aspect==="maintenance" ? "素材のメンテナンス" :  aspect==="sustainability" ? "持続可能性" :  ""}
                {:else}
                  {aspect}
                {/if}
              </button>
            {/each}
          </div>

          {#each Object.keys(formatted_feedback) as aspect}
            <div class="card container tab-content" class:active={activeAspect===aspect}>
              <SvelteMarkdown source={japanese ? japanese_formatted_feedback[aspect]['feedback'] : formatted_feedback[aspect]['feedback']} />
              
              <div class="card container">
                <h6> <b> <u>{japanese ? "ご提案": "Suggestions" }</u>  </b></h6>
                <div class="control" style="justify-content:space-between;">
                  {#if formatted_feedback[aspect]['suggestions'].length <= 0}
                    <p> {japanese ? "提案はない。" : "No suggestions provided."}  </p>
                  {:else}
                    {#each formatted_feedback[aspect]['suggestions'] as suggestion, i}
                      <div class="card container" style="height:100%;">
                        {#if suggestion[1] === "material" && suggestion.length===3} 
                          <span> <b> {japanese ? japanese_formatted_feedback[aspect]['suggestions'][i][0] : suggestion[0]} </b></span>
                          <DynamicImage imagepath={suggestion[2]} alt={suggestion[0]} size={"100px"} is_draggable={true}/>
                          <span> <b> {japanese ? "素材" : suggestion[1].charAt(0).toUpperCase() + suggestion[1].slice(1)}  </b></span>
                          <button  on:click={() => {generate(suggestion[0])}}> 
                            {japanese ? "もっと生み出せ！": "Generate more!"}
                            <img src="./logos/magic-wand-svgrepo-com.svg" style="width:25px; height:25px; align-items: center; justify-content: center;" alt="Generate">
                          </button>
                        {:else if suggestion[1] === "attachment" && suggestion.length===3}
                          <span> <b> {japanese ? japanese_formatted_feedback[aspect]['suggestions'][i][0] : suggestion[0]} </b></span>
                          <DynamicImage imagepath={suggestion[2]} alt={suggestion[0]} size={"100px"}/>
                          <span><b> {japanese ? "添付ファイル" : suggestion[1].charAt(0).toUpperCase() + suggestion[1].slice(1)}</b></span>
                        {:else if suggestion[1] === "finish" && suggestion.length===3}
                          <span> <b> {japanese ? japanese_formatted_feedback[aspect]['suggestions'][i][0] : suggestion[0]} </b></span>
                          <div class="card container">
                            <span> {japanese ? "不透明度：" : "Opacity:"} {suggestion[2]["opacity"]}</span>
                            <span> {japanese ? "粗さ：" : "Roughness:"}  {suggestion[2]["roughness"]}</span>
                            <span> {japanese ? "金属的だ：": "Metalness:"}  {suggestion[2]["metallic"]}</span>
                          </div>
                          <span><b> {japanese ? "素材仕上げ" : suggestion[1].charAt(0).toUpperCase() + suggestion[1].slice(1)} </b></span>
                          <button  on:click={() => {applyFinishSuggestion(suggestion[2])}}> {japanese ? "仕上げを施す" : "Apply Finish"}  </button>
                        {:else}
                          <span> <b> {japanese ? japanese_formatted_feedback[aspect]['suggestions'][i][0] : suggestion[0]} </b></span>
                          <span><b> {suggestion[1].charAt(0).toUpperCase() + suggestion[1].slice(1)} </b></span>
                        {/if} 
                      </div>
                    {/each}
                  {/if}

                  
                </div>
              </div>
            </div>
          {/each}
          
          <h6> <b> <u> {japanese ? "参考文献" : "References"}</u>  </b></h6>
          <SvelteMarkdown source={references} />
        {:else if is_loading_feedback}
          <div class="images-placeholder">
            {japanese ? 
              "フィードバックをリクエストしています。しばらくお待ちください。60〜90秒ほどかかる場合があります。" :
              "Requesting feedback, please wait. This may take around 60 to 90 seconds."
            }
            <Circle size="60" color="#FF3E00" unit="px" duration="1s" />
          </div>
        {:else}
          <p> {japanese ? "フィードバックはありません。" : "No feedback available."}  </p>
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
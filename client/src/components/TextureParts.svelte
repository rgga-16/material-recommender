<script>
    import {in_japanese, selected_objs_and_parts} from '../stores.js';
    import NumberSpinner from "svelte-number-spinner";
    import { Circle } from 'svelte-loading-spinners';
    import RangeSlider from "svelte-range-slider-pips";
    import {onMount} from 'svelte';
    
    export let texturepart_panels; 

    let isMouseDown=false;

    let opacity = [1.0];
    let roughness = [0.0];
    let metalness = [0.0];
    let normal_strength = [0.0];
    let height_strength = [0.0];

    let japanese;
    in_japanese.subscribe(value => {
        japanese = value;
    });


    let activeTab='adjust-finish';
    function switchTab(tab) {
        activeTab = tab;
    }

    function changeProperty(property, new_value, old_value=0) {

        for(const texturepart_panel in texturepart_panels) {
            texturepart_panel.changeProperty(property, new_value, old_value);
        }

    }

    function updateOpacities() {
        for(const texturepart_panel in texturepart_panels) {
            texturepart_panel.updateOpacity(opacity[0]);
            console.log(texturepart_panel.material_name);
        }
    }

    onMount(() => {
        console.log(texturepart_panels);
        console.log(texturepart_panels[0]);
    });
</script>

<div class="column centered gapped container">
    <div class="w3-bar w3-grey tabs">
        <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='adjust-finish'} on:click={()=>switchTab('adjust-finish')} id="adjust-finish-btn"> {japanese ? "素材仕上げ" : "Material Finish"} </button>
        <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='adjust-texture-map'} on:click={()=>switchTab('adjust-texture-map')} id="adjust-texture-btn"> {japanese ? "テクスチャマップ": "Texture Map"}</button>
        <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='adjust-color'} on:click={()=>switchTab('adjust-color')} id="adjust-color-btn"> {japanese ? "カラー仕上げ" : "Color Finish"}</button>
        <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='attached-parts'} on:click={()=>switchTab('attached-parts')} id="attached-parts-btn"> {japanese ? "付属部品" : "Attached Parts"}</button>
    </div>

    <div class="container column centered padded auto tab-content" class:active={activeTab==='adjust-finish'}>
        <h5><b> {japanese ? "素材仕上げの調整" : "Adjust Material Finish"}</b></h5> 
        <div class="row centered expand padded">
            <span> {japanese ? "不透明度：" : "Opacity:"}   </span>
            <div style="width:100%; align-items:inherit; justify-content:inherit;" on:mousedown={() => isMouseDown=true} on:mouseup = {() => {isMouseDown=false;changeProperty("opacity", opacity[0], 1.0)}}> 
                <RangeSlider on:change={() => updateOpacities(opacity[0])} bind:values={opacity} min={0} max={1} step={0.1} float={true} pips /> 
            </div>
        </div>
        <div class="row centered expand padded">
            <span> {japanese ? "粗さ：" : "Roughness:"} </span>
        
        </div>
        <div class="row centered expand padded">
            <span> {japanese ? "金属的だ：": "Metalness:"} </span>
        
        </div>
        <div class="row centered expand padded">
            <span> {japanese ? "法線マップの強度:" : "Normal Map Strength:"} </span>
        
        </div>
        <div class="row centered expand padded">
            <span> {japanese ? "高さマップの強度:" : "Height Map Strength:"} </span>
        
        </div>
    </div>

    <div class="container column centered padded auto  tab-content" class:active={activeTab==='adjust-texture-map'}>
    
    </div>

    <div class="container column centered padded auto  tab-content" class:active={activeTab==='adjust-color'}>
    
    </div>

    <div class="container column centered padded auto  tab-content" class:active={activeTab==='attached-parts'}>
    
    </div>

</div>


<style>
    .container {
        border: 1px solid black;
    }

    .auto {
        width: 100%;
        height: auto;
    }

    .expand {
        width: 100%;
        height: 100%;
    }

    

    .row {
        display: flex;
        flex-direction: row;
    }       

    .column {
        display: flex;
        flex-direction: column;
    }

    .centered {
        display: flex;
        justify-content: center;
        align-items: center;
        align-content: center;
    }

    .justified {
        justify-content: space-between;
    }

    .padded {
        padding: 5px;
        gap: 5px;
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

    .tab-content {
      display: none;
    }

    .tab-content.active {
        display: flex;
        flex-direction: column;
    }

</style>
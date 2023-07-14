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
    let normalScale = [0.0];
    let displacementScale = [0.0];

    let translationX = 0.0; 
    let translationY = 0.0;
    let rotation= 0.0; 
    let scale = 1.0;
    $:scaleX = scale; 
    $:scaleY =  scale; 


    let japanese;
    in_japanese.subscribe(value => {
        japanese = value;
    });


    let activeTab='adjust-finish';
    function switchTab(tab) {
        activeTab = tab;
    }

    function changeProperties(property, new_value, old_value=0) {

        for(const texturepart_panel of texturepart_panels) {
            texturepart_panel.changeProperty(property, new_value, old_value);
        }

    }

    function updateOpacities() {
        for(const texturepart_panel of texturepart_panels) {
            texturepart_panel.updateOpacity(opacity[0]);
        }
    }

    function updateRoughnesses() {
        for(const texturepart_panel of texturepart_panels) {
            texturepart_panel.updateRoughness(roughness[0]);
        }
    }

    function updateMetalnesses() {
        for(const texturepart_panel of texturepart_panels) {
            texturepart_panel.updateMetalness(metalness[0]);
        }
    }

    function updateNormalScales() {
        for(const texturepart_panel of texturepart_panels) {
            texturepart_panel.updateNormalScale(normalScale[0]);
        }
    }

    function updateDisplacementScales() {
        for(const texturepart_panel of texturepart_panels) {
            texturepart_panel.updateDisplacementScale(displacementScale[0]);
        }
    }

    function updateTextureMapOffsets(x_or_y,translation) {
        for(const texturepart_panel of texturepart_panels) {
            texturepart_panel.updateTextureMapOffset(x_or_y, translation);
        }
    }

    function updateTextureMapOrientations(rotation) {
        for(const texturepart_panel of texturepart_panels) {
            texturepart_panel.updateTextureMapOrientation(rotation);
        }
    }

    function updateTextureMapScales(x_or_y, scale) {
        for(const texturepart_panel of texturepart_panels) {
            texturepart_panel.updateTextureMapScale(x_or_y, scale);
        }
    }



    onMount(() => {
        console.log(texturepart_panels);
        console.log(texturepart_panels[0]);
    });
</script>

<div class="column centered gapped container">

    <div class="row centered padded"> 
        
        <b>Control Multiple Parts</b> 

    </div>

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
            <div style="width:100%; align-items:inherit; justify-content:inherit;" on:mousedown={() => isMouseDown=true} on:mouseup = {() => {isMouseDown=false;changeProperties("opacity", opacity[0], 1.0)}}> 
                <RangeSlider on:change={() => updateOpacities(opacity[0])} bind:values={opacity} min={0} max={1} step={0.1} float={true} pips /> 
            </div>
        </div>
        <div class="row centered expand padded">
            <span> {japanese ? "粗さ：" : "Roughness:"} </span>
            <div style="width:100%; align-items:inherit; justify-content:inherit;" on:mousedown={() => isMouseDown=true} on:mouseup = {() => {isMouseDown=false;changeProperties("roughness", roughness[0], 0.5)}}> 
                <RangeSlider on:change={() => updateRoughnesses(roughness[0])} bind:values={opacity} min={0} max={1} step={0.1} float={true} pips /> 
            </div>
        </div>
        <div class="row centered expand padded">
            <span> {japanese ? "金属的だ：": "Metalness:"} </span>
            <div style="width:100%; align-items:inherit; justify-content:inherit;" on:mousedown={() => isMouseDown=true} on:mouseup = {() => {isMouseDown=false;changeProperties("metalness", metalness[0], 0.5)}}> 
                <RangeSlider on:change={() => updateMetalnesses(metalness[0])} bind:values={opacity} min={0} max={1} step={0.1} float={true} pips /> 
            </div>
        </div>
        <div class="row centered expand padded">
            <span> {japanese ? "法線マップの強度:" : "Normal Scale:"} </span>
            <div style="width:100%; align-items:inherit; justify-content:inherit;" on:mousedown={() => isMouseDown=true} on:mouseup = {() => {isMouseDown=false;changeProperties("normalScale", normalScale[0], 0.5)}}> 
                <RangeSlider on:change={() => updateNormalScales(normalScale[0])} bind:values={opacity} min={0} max={10} step={0.1} float={true}/> 
            </div>
        </div>
        <div class="row centered expand padded">
            <span> {japanese ? "高さマップの強度:" : "Height Scale:"} </span>
            <div style="width:100%; align-items:inherit; justify-content:inherit;" on:mousedown={() => isMouseDown=true} on:mouseup = {() => {isMouseDown=false;changeProperties("displacementScale", displacementScale[0], 0.00)}}> 
                <RangeSlider on:change={() => updateDisplacementScales(displacementScale[0])} bind:values={opacity} min={0} max={0.5} step={0.01} float={true}/> 
            </div>
        </div>
    </div>

    <div class="container column centered padded auto  tab-content" class:active={activeTab==='adjust-texture-map'}>
        <div class="row centered padded expand">
            <div class="column centered padded auto container">
                <h6> <b> {japanese ? "平行移動": "Translation"} </b></h6>
                <div class="row centered expand padded" on:mousedown={() => isMouseDown=true} on:mouseup = {() => {isMouseDown=false; changeProperties("offsetX", translationX, 0.0)}}>
                    <span>X:</span>
                    <NumberSpinner on:change={() => updateTextureMapOffsets("x",translationX)} bind:value={translationX} min=0.0 max=20 step=0.01 decimals=1 precision=0.01/>
                </div>
                <div class="row centered expand padded" on:mousedown={() => isMouseDown=true} on:mouseup = {() => {isMouseDown=false; changeProperties("offsetY", translationY, 0.0)}}>
                    <span>Y:</span>
                    <NumberSpinner on:change={() => updateTextureMapOffsets("y",translationY)} bind:value={translationY} min=0.0 max=20 step=0.01 decimals=1 precision=0.01/>
                </div>
            </div>
            <div class="column centered padded auto container">
                <h6> <b> {japanese ? "回転": "Rotation"} </b></h6>
                <div class="row centered expand padded" on:mousedown={() => isMouseDown=true} on:mouseup = {() => {isMouseDown=false; changeProperties("rotation",rotation,0)}}>
                    <span>Z: </span>
                    <NumberSpinner on:change={() =>  updateTextureMapOrientations(rotation)} bind:value={rotation} min=0 max=360 step=0.1 decimals=1 precision=0.1/>°
                </div>
    
            </div>
            <div class="column centered padded auto container">
                <h6> <b> {japanese ? "スケール": "Scale"} </b></h6>
                <div class="row centered expand padded" on:mousedown={() => isMouseDown=true} on:mouseup = {() => {isMouseDown=false; changeProperties("scaleX",scale,1); changeProperties("scaleY",scale,1)}}>
                    <span>X & Y: </span>
                    <NumberSpinner on:change={() => {updateTextureMapScales("x",scale);updateTextureMapScales("y",scale)}} bind:value={scale} min=1 max=40 step=0.01 decimals=1 precision=0.01/>
                </div>
                <div class="row centered expand padded" on:mousedown={() => isMouseDown=true} on:mouseup = {() => {isMouseDown=false; changeProperties("scaleX",scaleX,1)}}>
                    <span>X: </span>
                    <NumberSpinner on:change={() => updateTextureMapScales("x",scaleX)} bind:value={scaleX} min=1 max=40 step=0.01 decimals=1 precision=0.01/>
                </div>
                <div class="row centered expand padded" on:mousedown={() => isMouseDown=true} on:mouseup = {() => {isMouseDown=false; changeProperties("scaleY",scaleY,1)}}>
                    <span>Y: </span>
                    <NumberSpinner on:change={() => updateTextureMapScales("y",scaleY)} bind:value={scaleY} min=1 max=40 step=0.01 decimals=1 precision=0.01/>
                </div>
            </div>
        </div>
    </div>

    <div class="container column centered padded auto  tab-content" class:active={activeTab==='adjust-color'}>
        <h5> <b> {japanese ? "カラー仕上げの調整": "Adjust Color Finish"}  </b></h5>
        
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
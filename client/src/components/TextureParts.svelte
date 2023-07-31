<script>
    import {in_japanese, selected_objs_and_parts, curr_texture_parts,saved_color_palettes} from '../stores.js';
    import {addToHistory} from '../main.js';
    import NumberSpinner from "svelte-number-spinner";

    import RangeSlider from "svelte-range-slider-pips";
    import {onMount} from 'svelte';
    import {get} from 'svelte/store';

    let sel_objs_and_parts;
    selected_objs_and_parts.subscribe(value => {
        sel_objs_and_parts = value;
    });

    let current_texture_parts;
    curr_texture_parts.subscribe(value => {
        current_texture_parts = value;
    });

    let japanese;
    in_japanese.subscribe(value => {
        japanese = value;
    });

    let isMouseDown=false;

    let opacity = [1.0];
    let roughness = [0.5];
    let metalness = [0.0];
    let normalScale = [0.0];
    let displacementScale = [0.0];
    let material_color="#FFFFFF"; 

    let translationX = 0.0; 
    let translationY = 0.0;
    let rotation= 0.0; 
    let scale = 1.0;
    $:scaleX = scale; 
    $:scaleY =  scale; 

    let material_color_palette;
    let palettes=[]; 
    saved_color_palettes.subscribe(value => {
        palettes=value;
    });
    let selected_palette_idx=0;
    let selected_swatch_idx = undefined;
    const no_color = {name: 'No Color', code: '#FFFFFF'}

    let isOpen=false;
    function toggleDropDown() {
        isOpen = !isOpen;
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
    

    


    let activeTab='adjust-finish';
    function switchTab(tab) {
        activeTab = tab;
    }

    function changeProperties(property, new_value, old_value=0) {

        for(let i = 0; i < sel_objs_and_parts.length; i++) {
            const parent = sel_objs_and_parts[i]["parent"];
            const name = sel_objs_and_parts[i]["name"];

            if(current_texture_parts[parent][name][property]) {
                old_value = current_texture_parts[parent][name][property];
            }
            curr_texture_parts.update(value => {
                value[parent][name][property] = new_value;
                return value;
            });

            addToHistory("Change " + property, 
                parent, name, 
                [property], 
                [old_value], 
                [new_value]
            );
        }

    }

    function updateColors() {
        let color = palettes[selected_palette_idx]['palette'][selected_swatch_idx];
        const hexNumber = parseInt(color.substring(1), 16);

        for(let i = 0; i < sel_objs_and_parts.length;i++) {
            selected_objs_and_parts.update(value => {
                value[i].model.children[0].material.color.setHex(hexNumber);
                value[i].model.children[0].material.color_hex = hexNumber;
                return value;
            });
        }
    }

    function updateOpacities(opacity_val) {
        for(let i =0; i < sel_objs_and_parts.length; i++) {
            selected_objs_and_parts.update(value => {
                value[i].model.children[0].material.transparent= true;
                value[i].model.children[0].material.opacity = opacity_val;
                return value;
            });
        }
    }

    function updateRoughnesses(roughness) {
        console.log(get(selected_objs_and_parts));

        for(let i =0; i < sel_objs_and_parts.length; i++) {
            selected_objs_and_parts.update(value => {
                value[i].model.children[0].material.roughness = roughness;
                return value;
            });
        }
    }

    function updateMetalnesses(metalness) {
        for(let i = 0; i < sel_objs_and_parts.length; i++) {
            selected_objs_and_parts.update(value => {
                value[i].model.children[0].material.metalness = metalness;
                return value;
            });
        }
    }

    function updateNormalScales(normalScale) {
        for(let index = 0; index < sel_objs_and_parts.length; index++) {
            selected_objs_and_parts.update(value => {
                value[index].model.children[0].material.normalScale.x = normalScale;
                value[index].model.children[0].material.normalScale.y = normalScale;
                return value;
            });
        }
    }

    function updateDisplacementScales(displacementScale) {
        for(let i = 0; i < sel_objs_and_parts.length; i++) {
            selected_objs_and_parts.update(value => {
                value[i].model.children[0].material.displacementScale = displacementScale;
                return value;
            });
        }
    }


    function setOffset(map,x_or_y, value) {
        map.offset[x_or_y] = value;
    }

    function updateTextureMapOffsets(x_or_y,translation) {

        for(let index = 0; index < sel_objs_and_parts.length;index++) {
            selected_objs_and_parts.update(value => {
                setOffset(value[index].model.children[0].material.map, x_or_y, translation)
                if (value[index].model.children[0].material.normalMap) {
                    setOffset(value[index].model.children[0].material.normalMap, x_or_y,translation);
                }
                if (value[index].model.children[0].material.aoMap) {
                    setOffset(value[index].model.children[0].material.aoMap, x_or_y,translation);
                }
                if (value[index].model.children[0].material.alphaMap) {
                    setOffset(value[index].model.children[0].material.alphaMap, x_or_y,translation);
                }
                if(value[index].model.children[0].material.emissiveMap) {
                    setOffset(value[index].model.children[0].material.emissiveMap, x_or_y,translation);
                }
                if (value[index].model.children[0].material.lightMap) {
                    setOffset(value[index].model.children[0].material.lightMap, x_or_y,translation);
                }
                if(value[index].model.children[0].material.metalnessMap) {
                    setOffset(value[index].model.children[0].material.metalnessMap, x_or_y,translation);
                }
                if(value[index].model.children[0].material.roughnessMap) {
                    setOffset(value[index].model.children[0].material.roughnessMap, x_or_y,translation);
                }
                if(value[index].model.children[0].material.displacementMap) {
                    setOffset(value[index].model.children[0].material.displacementMap, x_or_y,translation);
                }
                if(value[index].model.children[0].material.bumpMap) {
                    setOffset(value[index].model.children[0].material.bumpMap, x_or_y,translation);
                }
                if(value[index].model.children[0].material.envMap) {
                    setOffset(value[index].model.children[0].material.envMap, x_or_y,translation);
                }
                return value;
            });
        }
    }


    function radianToDegree(radians) {
      return radians * (180/Math.PI);
    }
    function degreeToRadians(degrees) {
      return degrees * (Math.PI/180);
    }
    function setOrientation(map,rot) {
        map.rotation = degreeToRadians(rot);
    }
    function updateTextureMapOrientations(rotation) {

        for(let index=0; index < sel_objs_and_parts.length; index++) {
            selected_objs_and_parts.update(value => {
                setOrientation(value[index].model.children[0].material.map,rotation);
                if (value[index].model.children[0].material.normalMap) {
                    setOrientation(value[index].model.children[0].material.normalMap,rotation);
                }
                if (value[index].model.children[0].material.aoMap) {
                    setOrientation(value[index].model.children[0].material.aoMap,rotation);
                }
                if (value[index].model.children[0].material.alphaMap) {
                    setOrientation(value[index].model.children[0].material.alphaMap,rotation);
                }
                if(value[index].model.children[0].material.emissiveMap) {
                    setOrientation(value[index].model.children[0].material.emissiveMap,rotation);
                }
                if (value[index].model.children[0].material.lightMap) {
                    setOrientation(value[index].model.children[0].material.lightMap,rotation);
                }
                if(value[index].model.children[0].material.metalnessMap) {
                    setOrientation(value[index].model.children[0].material.metalnessMap,rotation);
                }
                if (value[index].model.children[0].material.bumpMap) {
                    setOrientation(value[index].model.children[0].material.bumpMap,rotation);
                }
                if(value[index].model.children[0].material.displacementMap) {
                    setOrientation(value[index].model.children[0].material.displacementMap,rotation);
                }
                if(value[index].model.children[0].material.envMap) {
                    setOrientation(value[index].model.children[0].material.envMap,rotation);
                }
                if(value[index].model.children[0].material.normalMap) {
                    setOrientation(value[index].model.children[0].material.normalMap,rotation);
                }
                if (value[index].model.children[0].material.roughnessMap) {
                    setOrientation(value[index].model.children[0].material.roughnessMap,rotation);
                }
                return value
            });
        }
    }

    function setScale(map, x_or_y, value) {
        map.repeat[x_or_y] = value;
    }

    function updateTextureMapScales(x_or_y, scale) {

        for(let index = 0; index < sel_objs_and_parts.length; index++) {
            selected_objs_and_parts.update(value => {
                setScale(value[index].model.children[0].material.map, x_or_y, scale);
                if (value[index].model.children[0].material.normalMap) {
                    setScale(value[index].model.children[0].material.normalMap, x_or_y, scale);
                }
                if (value[index].model.children[0].material.aoMap) {
                    setScale(value[index].model.children[0].material.aoMap, x_or_y, scale);
                }
                if (value[index].model.children[0].material.alphaMap) {
                    setScale(value[index].model.children[0].material.alphaMap, x_or_y, scale);
                }
                if(value[index].model.children[0].material.emissiveMap) {
                    setScale(value[index].model.children[0].material.emissiveMap, x_or_y, scale);
                }
                if (value[index].model.children[0].material.lightMap) {
                    setScale(value[index].model.children[0].material.lightMap, x_or_y, scale);
                }
                if(value[index].model.children[0].material.metalnessMap) {
                    setScale(value[index].model.children[0].material.metalnessMap, x_or_y, scale);
                }
                if(value[index].model.children[0].material.roughnessMap) {
                    setScale(value[index].model.children[0].material.roughnessMap, x_or_y, scale);
                }
                if(value[index].model.children[0].material.displacementMap) {
                    setScale(value[index].model.children[0].material.displacementMap, x_or_y, scale);
                }
                if(value[index].model.children[0].material.bumpMap) {
                    setScale(value[index].model.children[0].material.bumpMap, x_or_y, scale);
                }
                if(value[index].model.children[0].material.envMap) {
                    setScale(value[index].model.children[0].material.envMap, x_or_y, scale);
                }
                return value;
            });
        }
    }


    // function onMouseDown(event) {
    //     if (event.button === 0) {
    //         mouseDown = true;

    //     }
    // }

    // function onMouseUp(event) {
    //     if(event.button===0) {
    //         mouseDown = false;

    //     }
    // }


    onMount(() => {
        if(material_color) {
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

        // window.addEventListener('mousedown', onMouseDown);
        // window.addEventListener('mouseup', onMouseUp);
    });
</script>

<div class="column centered gapped container">

    <div class="row centered padded"> 
        
        {#if japanese} 
            <h4>複数のオブジェクトを制御する</h4>
        {:else}
            <h4>Control Multiple Objects</h4>
        {/if}

    </div>

    <div class="w3-bar w3-grey tabs">
        <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='adjust-finish'} on:click={()=>switchTab('adjust-finish')} id="adjust-finish-btn"> {japanese ? "素材の仕上げ" : "Material Finish"} </button>
        <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='adjust-texture-map'} on:click={()=>switchTab('adjust-texture-map')} id="adjust-texture-btn"> {japanese ? "テクスチャマップ": "Texture Map"}</button>
        <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='adjust-color'} on:click={()=>switchTab('adjust-color')} id="adjust-color-btn"> {japanese ? "カラー仕上げ" : "Color Finish"}</button>
    </div>

    <div class="container column centered padded auto tab-content" class:active={activeTab==='adjust-finish'}>
        <h5><b> {japanese ? "素材仕上げの調整" : "Adjust Material Finish"}</b></h5> 
        <div class="row centered expand padded">
            <span> {japanese ? "透明度：" : "Opacity:"}   </span>
            <div style="width:100%; align-items:inherit; justify-content:inherit;" on:mousedown={() => isMouseDown=true} on:mouseup = {() => {isMouseDown=false;changeProperties("opacity", opacity[0], 1.0)}}> 
                <RangeSlider on:change={() => updateOpacities(opacity[0])} bind:values={opacity} min={0} max={1} step={0.1} float={true} pips /> 
            </div>
        </div>
        <div class="row centered expand padded">
            <span> {japanese ? "光沢：" : "Roughness:"} </span>
            <div style="width:100%; align-items:inherit; justify-content:inherit;" on:mousedown={() => isMouseDown=true} on:mouseup = {() => {isMouseDown=false;changeProperties("roughness", roughness[0], 0.5)}}> 
                <RangeSlider on:change={() => updateRoughnesses(roughness[0])} bind:values={roughness} min={0} max={1} step={0.1} float={true} pips /> 
            </div>
        </div>
        <div class="row centered expand padded">
            <span> {japanese ? "金属度：": "Metalness:"} </span>
            <div style="width:100%; align-items:inherit; justify-content:inherit;" on:mousedown={() => isMouseDown=true} on:mouseup = {() => {isMouseDown=false;changeProperties("metalness", metalness[0], 0.5)}}> 
                <RangeSlider on:change={() => updateMetalnesses(metalness[0])} bind:values={metalness} min={0} max={1} step={0.1} float={true} pips /> 
            </div>
        </div>
        <div class="row centered expand padded">
            <span> {japanese ? "法線マップの強度:" : "Normal Scale:"} </span>
            <div style="width:100%; align-items:inherit; justify-content:inherit;" on:mousedown={() => isMouseDown=true} on:mouseup = {() => {isMouseDown=false;changeProperties("normalScale", normalScale[0], 0.5)}}> 
                <RangeSlider on:change={() => updateNormalScales(normalScale[0])} bind:values={normalScale} min={0} max={10} step={0.1} float={true}/> 
            </div>
        </div>
        <div class="row centered expand padded">
            <span> {japanese ? "高さマップの強度:" : "Height Scale:"} </span>
            <div style="width:100%; align-items:inherit; justify-content:inherit;" on:mousedown={() => isMouseDown=true} on:mouseup = {() => {isMouseDown=false;changeProperties("displacementScale", displacementScale[0], 0.00)}}> 
                <RangeSlider on:change={() => updateDisplacementScales(displacementScale[0])} bind:values={displacementScale} min={0} max={0.5} step={0.01} float={true}/> 
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

        <div class="row centered expand padded container" id="color-palette-header">
            <label class="swatch selectable" class:selected={selected_swatch_idx===undefined} style="background-color: {no_color.code};">
                <img src="./logos/cancel-svgrepo-com.svg" alt="">
                <input type=radio bind:group={selected_swatch_idx} name={no_color.name} value={undefined}>
            </label>

            <div class="row centered expand padded" style="position: relative;">
                {#if selected_palette_idx != undefined && palettes.length > 0}
                    {#each palettes[selected_palette_idx]['palette'] as swatch, i }
                        <label class="swatch selectable" style="background-color: {swatch};" class:selected={selected_swatch_idx===i}>
                            <input type=radio bind:group={selected_swatch_idx} name={swatch} value={i} on:change={() => {updateColors();changeProperties("color",palettes[selected_palette_idx]['palette'][selected_swatch_idx],"#FFFFFF")}}>
                        </label>
                    {/each}
                {/if}

                {#if isOpen}
                    <div class="dropdown-list" style="position: absolute; top: 30px; left: 170px; z-index=1;">
                        {#each palettes as p,j}
                            <label class="row centered expand padded container palette selectable" class:selected={selected_palette_idx===j}>
                                {#each p["palette"] as swatch}
                                    <div class="swatch" style="background-color: {swatch};"></div>
                                {/each}
                                <input type=radio bind:group={selected_palette_idx} name={j} value={j} on:change={() => {selected_swatch_idx=0; updateColors();changeProperties("color",palettes[selected_palette_idx]['palette'][selected_swatch_idx],"#FFFFFF")}}>
                            </label>
                        {/each}
                        <button on:click|preventDefault={() => addNewColorPalete()}> 
                            {japanese ? "新規追加" : "Add new"} 
                            <img src="./logos/add-svgrepo-com.svg" style="width:25px; height:25px; align-items: center; justify-content: center;" alt="Add new color palette">
                        </button>
                    </div>
                {/if}
            </div>

            <!-- svelte-ignore a11y-click-events-have-key-events -->
            <div style=" width: 25px; height: 25px; align-items: center; justify-content: center; cursor: pointer;" on:click={() => toggleDropDown()}> 
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
            on:change={() => {updateColors(); changeProperties("color", palettes[selected_palette_idx]['palette'][selected_swatch_idx], "#FFFFFF")}}
            on:mousedown={() => {isMouseDown=true}} 
            on:mouseup = {() => {isMouseDown=false}}
            >
        {/if}
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

</style>
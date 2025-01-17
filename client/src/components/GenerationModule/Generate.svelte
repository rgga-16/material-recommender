<script>
    import {onMount} from 'svelte';
    import { Circle } from 'svelte-loading-spinners';
    import NumberSpinner from "svelte-number-spinner";
    import GeneratedTextures from './GeneratedTextures.svelte';
    import {curr_rendering_path} from '../../stores.js';
    import {curr_texture_parts} from '../../stores.js';
	import {curr_textureparts_path} from '../../stores.js';
    import {generate_tab_page} from '../../stores.js';
    import {generated_texture_name} from '../../stores.js';
    import { get } from 'svelte/store';
    import {action_history} from '../../stores.js';
    import { threed_display_global } from '../../stores.js';

    import {transferred_texture_url} from '../../stores.js';
    import {transferred_textureimg_url} from '../../stores.js';
    import {transferred_texture_name} from '../../stores.js';
    import {in_japanese} from '../../stores.js';

    import {addToHistory} from '../../main.js';
    import {translate} from '../../main.js';
    import {getImage} from '../../main.js';
    import {isDict, dictToString} from '../../main.js';

    let history; 
    action_history.subscribe(value => {
        history = value;
    });

    let japanese;
    in_japanese.subscribe(value => {
        japanese = value;
    });

    let three_display;
    threed_display_global.subscribe(value => {
        three_display = value;
    });

    export let onCallUpdateCurrentRendering
    function callUpdateCurrentRendering() {
        onCallUpdateCurrentRendering();
    }

    let input_material='';

    let selected_object_parts=[]; 
    let objs_and_parts = {}
    let selected_obj_parts_dict = {}

    let rendering_texture_pairs=[];

    let is_loading;
    let texture_history = [];
    let generated_textures = [];
    let selected_textures = [];
    let selected_texture;

    let is_collapsed_keywords = true;

    let selected_index;

    let n_textures = 4;
    
    let activeTab = "generated";

    onMount(async () => {
        // const obj_and_part_resp= await fetch('./get_objects_and_parts');
        // const obj_and_part_json = await obj_and_part_resp.json(); 
        // objs_and_parts = obj_and_part_json;
    }); 

    async function generate_similar_textures(texture_str) {
        input_material = texture_str
        is_loading=true; 
        generated_textures=[];

        let input = Object.assign("",texture_str);
        let material = Object.assign("",texture_str);
        if (isDict(input)) {
            input = dictToString(input);
        }
        
        let keywords = Object.assign([],selected_prompt_keywords);

        if(keywords.length > 0) {
            for (let i = 0; i < keywords.length; i++) {
                let temp = keywords[i];
                if(isDict(temp)) {
                    temp = dictToString(temp);
                    material = dictToString(material);
                }
                input += ", " + temp;
            }
        }
        if(japanese) {
            console.log(input);
            input = await translate("JA", "EN-US", input);
            material = await translate("JA", "EN-US", material);
        }
        input += ",  texture map, seamless, 4k";
        console.log(input);

        const results_response = await fetch("/generate_similar_textures", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                "texture_string": input,
                "n":n_textures,
                "imsize":448,
                "impath":selected_texture,
            }),
        });
        selected_texture=null;
        const results_json = await results_response.json();
        generated_textures = results_json["results"];
        is_loading=false;
        generated_texture_name.set(material);
    }

    export async function generate_textures(texture_str) {
        input_material=texture_str;
        is_loading=true; 
        selected_texture=null;
        generated_textures=[];

        let input = Object.assign("",texture_str);
        let material = Object.assign("",texture_str);
        if (isDict(input)) {
            input = dictToString(input);
            material = dictToString(material);
        }

        console.log(input);
        let keywords = Object.assign([],selected_prompt_keywords);

        if(keywords.length > 0) {
            for (let i = 0; i < keywords.length; i++) {
                let temp = keywords[i];
                if(isDict(temp)) {
                    temp = dictToString(temp);
                }
                input += ", " + temp;
            }
        }

        if(japanese) {
            console.log(input);
            input = await translate("JA", "EN-US", input);
            material = await translate("JA", "EN-US", material);
        }
        input += ",  texture map, seamless, 4k";
        console.log(input);

        const results_response = await fetch("/generate_textures", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                "texture_string": input,
                "n":n_textures,
                "imsize":448,
            }),
        });
        
        const results_json = await results_response.json();
        generated_textures = results_json["results"];
        is_loading=false;
        generated_texture_name.set(material);

        texture_history.append({
            "texture_string": input,
            "textures": generated_textures
        })
        
    }

    
    const n_pages = 4;

    let current_page = 0;
    generate_tab_page.subscribe(value=> {
        current_page=value;
    });

    let active_obj_id=0;
    function switchObjectTab(id) {
        active_obj_id=id;
    }

    //This function reverts back to the first page of the Generation module.
    export function reset_page() {
        current_page=0;
        generate_tab_page.set(0);
        switchTab("generated");
        generated_textures=[];
        rendering_texture_pairs=[];
        selected_textures = [];
        switchObjectTab(0);
        selected_object_parts=[];
        selected_index=undefined;

    }

    function switchTab(tab) {
        activeTab=tab;
    }

    let brainstormed_prompt_keywords = []; //Keywords that are generated by the AI assistant
    let manual_prompt_keywords = []; //Keywords that the user manually added
    // $: prompt_keywords = [...brainstormed_prompt_keywords, ...manual_prompt_keywords];

    let selected_prompt_keywords = [];
    let is_loading_keywords = false;

    let keyword="";

    export function empty_keywordlists() {
        keyword="";
        brainstormed_prompt_keywords = [];
        manual_prompt_keywords = [];
        selected_prompt_keywords = [];
    }

    function del_manual_keyword(index, keyword) {
        manual_prompt_keywords.splice(index, 1);
        manual_prompt_keywords=manual_prompt_keywords;

        if (selected_prompt_keywords.includes(keyword)) {
            let indices = selected_prompt_keywords.map((e,i) => e === keyword ? i : '').filter(String);

            for (let i = 0; i < indices.length; i++) {
                selected_prompt_keywords.splice(indices[i], 1);
                selected_prompt_keywords=selected_prompt_keywords;
            }
        }

    }

    function del_brainstormed_keyword(index, keyword) {
        brainstormed_prompt_keywords.splice(index, 1);
        brainstormed_prompt_keywords=brainstormed_prompt_keywords;

        if (selected_prompt_keywords.includes(keyword)) {
            let indices = selected_prompt_keywords.map((e,i) => e === keyword ? i : '').filter(String);

            for (let i = 0; i < indices.length; i++) {
                selected_prompt_keywords.splice(indices[i], 1);
                selected_prompt_keywords=selected_prompt_keywords;
            }
        }

    }

    function add_keyword(k) {
        if(k.trim() === '') {
            alert(japanese ? "キーワードを入力してください。" :"Please type in a keyword.");
            return;
        }
        manual_prompt_keywords.push(k);
        manual_prompt_keywords=manual_prompt_keywords;

        selected_prompt_keywords.push(k);
        selected_prompt_keywords=selected_prompt_keywords;

        keyword="";
        
    }

    async function brainstorm_prompt_keywords() {
        if (input_material.trim() === '') {
            alert(japanese ? "素材を入力してください。" : "Please type in a material.");
            return;
        }
        brainstormed_prompt_keywords=[];
        selected_prompt_keywords=[];
        is_loading_keywords=true;
        const response = await fetch("/brainstorm_prompt_keywords", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                "texture_string": input_material,
            }),
        });
        const json = await response.json();
        
        brainstormed_prompt_keywords = json["brainstormed_prompt_keywords"];

        if (japanese) {
            for(let i = 0; i < brainstormed_prompt_keywords.length; i++) {
                let k = brainstormed_prompt_keywords[i];
                brainstormed_prompt_keywords[i] = await translate("EN","JA",k);
            }
        }
        is_loading_keywords=false;
    }
</script>

<div class="material_generator">
    <h3> {japanese ? "素材ジェネレーター" : "Material Generator"}  </h3>

    <div class="page" class:hidden={current_page!=0} id="generate_materials">
        <div class="row">
            <input name="material_name" type="text" bind:value={input_material} 
            on:keydown={(event) => {
                if (event.key === 'Enter') {
                    generate_textures(input_material);
                }
            }} 
            placeholder={japanese ? "素材を入力してください..." : "Type in a material..."} required/>
            <div class="column">
                <span> {japanese ? "テクスチャマップの数：": "No. of texture maps:"}  </span>
                <NumberSpinner bind:value={n_textures} min={1} max={10} step=1/>
            </div>
        </div>

        <div class="column" id="prompt_keywords" style="border: solid 1px black;">
            <!-- svelte-ignore a11y-click-events-have-key-events -->
            <div class="row" id="keywords-header" on:click={() => {is_collapsed_keywords=!is_collapsed_keywords}} style="cursor:pointer;width:100%;"> 
                {#if japanese} 
                    "{input_material.trim() !== '' ? input_material : ''}"にキーワードを追加
                {:else}
                    Add keywords to "{input_material.trim() !== '' ? input_material : ''}"
                {/if}
                
                
                {#if is_collapsed_keywords===true}
                    <img src="./logos/down-arrow-svgrepo-com.svg" style="width:25px; height: 25px;" alt="Expand">
                {:else}
                    <img src="./logos/up-arrow-svgrepo-com.svg" style="width:25px; height: 25px;" alt="Collapse">
                {/if}
            </div>
                <div class="row" class:collapsed={is_collapsed_keywords===true}>
                    <div class="column">
                        <div class="row"> 
                            <input type="text" style="width:65%;" bind:value={keyword} 
                            on:keydown={(event)=> {
                                if (event.key === 'Enter') {
                                    add_keyword(keyword);
                                }
                            }} 
                            placeholder={japanese ? "キーワードを入力してください..." : "Type in a keyword..."}> 
                            <button on:click|preventDefault={()=>add_keyword(keyword)}>
                                {japanese ? "追加" : "Add"}
                                <img src="./logos/add-svgrepo-com.svg" style="width:18px; height:18px; align-items: center; justify-content: center;" alt="Add keyword">
                            </button>
                        </div>
                        <div class="row">
                            <button on:click|preventDefault={brainstorm_prompt_keywords} style="margin-right: 10px;"> 
                                {#if japanese} 
                                    "{input_material}"のキーワードをブレインストーミングする 
                                {:else}
                                    Brainstorm keywords for "{input_material}" 
                                {/if}
                            </button>

                            <button on:click|preventDefault={()=>{empty_keywordlists();}}> 
                                {japanese ? "キーワードをクリアする" : "Clear keywords"}
                            </button>
                        </div>
                    </div>
                    <div class="row" style="flex-wrap:wrap; overflow:auto;">
                        {#if manual_prompt_keywords.length > 0}
                            {#each manual_prompt_keywords as manual_keyword,i}
                                <label class="tag" class:selected={selected_prompt_keywords.includes(manual_keyword)} >
                                    <input type="checkbox" value={manual_keyword} bind:group={selected_prompt_keywords} />
                                    +"{manual_keyword}"
                                    <button on:click={()=>del_manual_keyword(i, manual_keyword)}>X</button>
                                </label>
                            {/each}
                        {/if}

                        {#if brainstormed_prompt_keywords.length > 0}
                            {#each brainstormed_prompt_keywords  as keyword,j}
                                <label class="tag" class:selected={selected_prompt_keywords.includes(keyword)}>
                                    <input type="checkbox" value={keyword} bind:group={selected_prompt_keywords} />
                                    +"{keyword}"
                                    <button on:click={()=>del_brainstormed_keyword(j, keyword)}>X</button>
                                </label>
                            {/each}
                        {:else if is_loading_keywords}
                            <div class="images-placeholder" style="height:20%;">
                                {japanese ? "キーワードを考える" : "Brainstorming keywords..."}
                                <Circle size="30" color="#FF3E00" unit="px" duration="1s" />
                            </div>
                        {/if}
                        {#if brainstormed_prompt_keywords.length <= 0 && manual_prompt_keywords.length <= 0}
                            <p> 
                                {japanese ? "キーワードは追加されていない。" : "No keywords added."}"
                            </p>
                        {/if}
                    </div>

                </div>
        </div>

        <div class="row">
            <button disabled={!selected_texture} on:click|preventDefault={() => generate_similar_textures(input_material)}> 
                {japanese ? "類似素材テクスチャを生成する"  : "Generate Similar Textures"}
            </button>
            <button on:click|preventDefault={() => generate_textures(input_material)}> 
                {japanese ? "素材テクスチャを生成する" : "Generate Textures"} 
            </button>
        </div>

        <div class="row">
            <!-- <div class="w3-bar w3-grey tabs column" style="width:50px;height:500px;" >
                <button class="w3-bar-item w3-button tab-btn" class:active={activeTab==='generated'} on:click={() => switchTab('generated')} id="generated-tabs">
                    Generated
                </button>
                <button class="w3-bar-item w3-button tab-btn" class:active={activeTab==='history'} on:click={() => switchTab('history')} id="generated-tabs">
                    History
                </button>
                <button class="w3-bar-item w3-button tab-btn" class:active={activeTab==='saved'} on:click={() => switchTab('saved')} id="generated-tabs">
                    Saved
                </button>
            </div> -->

            <div class="column">
                {#if generated_textures.length > 0}
                    <p> 
                        {#if japanese}
                            {input_material}のテクスチャマップの結果
                        {:else}
                            Texture map results for: {input_material}
                        {/if}
                    </p>
                    <GeneratedTextures pairs= {generated_textures} texture_name={get(generated_texture_name)} bind:selected_texture={selected_texture}/>
                {:else if is_loading==true}
                    <div class="images-placeholder">
                        {japanese ? "テクスチャを生成しています。お待ちください。" : "Generating textures, please wait."}
                        <Circle size="60" color="#FF3E00" unit="px" duration="1s" />
                    </div>
                {:else}
                    <div class="images-placeholder">
                        <pre> {japanese ? "素材テクスチャはまだ生成されていない。" : "No material textures generated yet."} 
                        </pre>
                    </div>
                {/if}
            </div>


        </div>

        


    </div>

</div>

<style>

    .tabs {
        width:100%;
        height: 100%;
        align-content:center;
        gap:0px;
    }

    .tab-btn {
        width: auto;
        height: 100%;
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

    #generated-tabs {
        transform:rotate(270deg);
    }

    .tab-content.active {
		display: flex;
        flex-direction: row;
        height: 100%;
        width:100%;
        padding: 5px;
        overflow: auto;
	}

    .material_generator {
        display: flex;
        align-items:center;
        justify-content:center;
        flex-direction: column;
        width:100%;
        height: 100%; 
        /* overflow: hidden; */
        text-align: center;
    }

    .row {
        display:flex; 
        flex-direction: row;
        align-items: center;
        justify-content: center;
        gap: 5px;
        padding: 5px;
    }

    .column {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 5px;
        padding: 5px;
    }

    
    .material_generator div.page{
        text-align: center;
        align-items: center;
        justify-content: center;
        overflow:auto;
        width:100%;
        height: 100%; 
    }   

    .material_generator .page.hidden{
        display:none;
    }

    .material_generator .page .carousel-nav-btns {
        padding:5px;
    }


    input[type="radio"] {
        display: none;
    }
    
    label {
        padding: 5px;
    }

    input[type="radio"]:checked + label {
        background-color: white;
    }

    .checkbox-group {
        width:100%;
        max-width:900px;
        margin:0 auto;
        text-align:left;
    }
    .checkbox-item {
        display: inline-block;
        margin:5px;
        background-color:lightblue;
    }
    
    .images-placeholder {
        width: 100%;
        height: 500px;
        border: 1px dashed black;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
    }

    .tag {
        background-color:lightgreen;
    }

    .tag input[type="checkbox"] {
        opacity: 0;
        position: fixed;
        width:0; 
    } 

    .selected {
        border: 2.5px solid blue;
    }

    .selected:hover {
        border: 2.5px solid blue;
    }

    .tag:hover{
        cursor:pointer;
        border: 2px solid grey;
    }

    .collapsed {
        display:none;
    }
</style>



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
    let generated_textures = [];
    let selected_textures = [];
    let selected_texture;

    let is_collapsed_keywords = true;

    let selected_index;

    let n_textures = 4;

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

        // generated_texture_name.set(input_material);
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

        // generated_texture_name.set(input_material);
        generated_texture_name.set(material);
        
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

        generated_textures=[];
        rendering_texture_pairs=[];
        selected_textures = [];
        switchObjectTab(0);
        selected_object_parts=[];
        selected_index=undefined;

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
            alert("Please type in a keyword.");
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
            alert("Please type in a material.");
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
        is_loading_keywords=false;
        brainstormed_prompt_keywords = json["brainstormed_prompt_keywords"];

        if (japanese) {
            for(let i = 0; i < brainstormed_prompt_keywords.length; i++) {
                let k = brainstormed_prompt_keywords[i];
                brainstormed_prompt_keywords[i] = await translate("EN","JA",k);
            }
        }
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
                    <NumberSpinner bind:value={n_textures} min={1} max={20} step=1/>
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

<style>

    .tab-btn {
        height:100%;
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

<!-- OLD CODE BELOW-->
<!--     
<div class="page" class:hidden={current_page!=1} id="apply_textures">
    <form on:submit|preventDefault={()=>apply_textures()}>
        <h4> Apply textures to rendering</h4>
        {#await objs_and_parts}
            <pre>Loading object names and their part names</pre>
        {:then data} 
            <div class="w3-bar w3-grey tabs">
                {#each Object.entries(data) as [obj_name, attribs],i}
                    <button class="w3-bar-item w3-button tab-btn" class:active={active_obj_id===i} on:click|preventDefault={()=>switchObjectTab(i)}> {obj_name} </button>
                {/each}
            </div>

            {#each Object.entries(data) as [obj_name,attribs], i}
                <div class="tab-content" class:active={active_obj_id===i}>
                    <div class="checkbox-group">
                        {#each attribs.parts.names as part_name}
                            <div class="checkbox-item">
                                <label for="checkbox-{part_name}"> 
                                    <input type="checkbox" bind:group={selected_object_parts} id="checkbox-{obj_name}-{part_name}" 
                                    name="checkbox-group-{obj_name}" value="{obj_name}-{part_name}" >
                                    {part_name} 
                                </label>
                            </div>
                        {/each}
                    </div>
                </div>
            {/each}
        {/await}
        <button> Apply textures </button>
    </form>
    {#if rendering_texture_pairs.length > 0}
            <GeneratedRenderings pairs= {rendering_texture_pairs} bind:selected_index={selected_index} />
            {#if selected_index!=undefined}
                <p> Rendering #{selected_index} selected. </p>
            {:else }
                <p> Please select a rendering to proceed.</p>
            {/if}
    {:else if is_loading==true}
        <div class="images-placeholder">
            Generating texture maps...
            <Circle size="60" color="#FF3E00" unit="px" duration="1s" />
        </div>
    {:else}
        <div class="images-placeholder">
            <pre>No renderings generated yet.</pre>
        </div>
    {/if}
    
    <div class="carousel-nav-btns">
        <button on:click|preventDefault={()=>prev_page()}> Back </button>
        <button disabled={!(selected_index!=undefined && rendering_texture_pairs.length > 0)} on:click|preventDefault={()=>next_page()}> Next </button>
    </div>
</div>

<div class="page" class:hidden={current_page!=2} id="refine_textures">
    {#if selected_index!=undefined && rendering_texture_pairs.length > 0}
        <RefineTexture bind:selected_index={selected_index} 
        bind:rendering_texture_pairs={rendering_texture_pairs} 
        objs_and_parts={objs_and_parts} 
        bind:selected_objs_and_parts_dict={selected_obj_parts_dict}/>
    {/if}
    
    <div class="carousel-nav-btns">
        <button on:click|preventDefault={()=>prev_page()}> Back </button>
        <button on:click|preventDefault={()=>apply_to_curr_rendering(selected_index)}> Apply to current rendering </button>
    </div>
</div> -->


<!-- <script>
    function next_page() {
        current_page+=1;
        if (current_page >= n_pages) {
            current_page=n_pages-1;
        }
    }

function prev_page() {
    current_page-=1;
    if(current_page < 0){
        current_page=0;
    }
}

async function apply_textures() {
        rendering_texture_pairs=[];
        selected_obj_parts_dict = {};
        if (selected_object_parts.length <= 0) { alert("Please select at least 1 object part"); return }
        is_loading=true;
        for (let i = 0; i < selected_object_parts.length; i++) {
            let splitted = selected_object_parts[i].split("-");
            let obj = splitted[0];
            let part = splitted[1];
            if(obj in selected_obj_parts_dict) {
                selected_obj_parts_dict[obj].push(part);
            } else {
                selected_obj_parts_dict[obj] = [part]; 
            }
        }
        const results_response = await fetch("/apply_textures", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                "obj_parts_dict": selected_obj_parts_dict,
                "selected_texturepaths":selected_textures,
                "texture_string":input_material
            }),
        });
        const results_json = await results_response.json();
        rendering_texture_pairs = results_json["results"];
        is_loading=false;
    }

    async function apply_to_curr_rendering(index) {
        // console.log("apply to curr rendering");
        if(index==undefined) {
            alert("Please select one of the options"); 
            return;
        }
        let selected_render_texture_pair = rendering_texture_pairs[index];
        let selected_rendering_path = selected_render_texture_pair.rendering; 
        let selected_texture_path = selected_render_texture_pair.texture; 
        let selected_rendering_info = selected_render_texture_pair.info; 
        let selected_info_path = selected_render_texture_pair.info_path;
        const response = await fetch("/apply_to_current_rendering", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                "rendering_path": selected_rendering_path,
                "texture_parts":selected_rendering_info,
                "textureparts_path": selected_info_path
            }),
        });

        const json = await response.json();
        curr_rendering_path.set(json["rendering_path"]);
        curr_texture_parts.set(await json["texture_parts"]);
		curr_textureparts_path.set(await json["textureparts_path"]);

        callUpdateCurrentRendering();
    }

</script> -->


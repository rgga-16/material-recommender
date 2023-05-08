<script>
    import MaterialCard from "./MaterialCard.svelte";
    import { Circle } from 'svelte-loading-spinners';
    import {actions_panel_tab} from '../../stores.js';
    import {generate_tab_page} from '../../stores.js';
    import {createEventDispatcher} from 'svelte';


    const dispatch = createEventDispatcher();

    const material_types = ["All types","wood","metal","fabric","ceramic"]
    const interior_design_styles = ['Modern', 'Traditional', 'Contemporary', 'Industrial', 'Transitional', 'Rustic', 'Bohemian', 'Minimalist', 'Hollywood Regency', 'Scandinavian']

    let selected_material_type;
    let selected_style;

    let suggested_materials=[];
    let selected_material_index;

    let activeTab='by_id_style';
    function switchTab(tab) {
        activeTab = tab;
    }
    let is_loading=false;

    async function suggest_by_style(material_type,style){
        is_loading=true;
        let material_suggest_dict = {
            "style":style,
            "material_type":material_type
        }
        suggested_materials=[];

        const material_suggestions_response = await fetch("/suggest_materials_by_style", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(material_suggest_dict),
        });
        const material_suggestions_json = await material_suggestions_response.json();
        suggested_materials = await material_suggestions_json;
        is_loading=false;

    }

    function switchActionPanelTab(tab) {
        actions_panel_tab.set(tab);
    }

    function switchGenerateTabPage(page_num) {
        generate_tab_page.set(page_num);
    }

    function proceed_to_generate(material_name) {
        switchActionPanelTab('generate');
        switchGenerateTabPage(0);
        dispatch('proceedToGenerate', material_name);
    }

</script>

    <h4>Suggest Materials</h4>

    <div class="w3-bar w3-grey tabs">
        <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='by_id_style'} on:click={()=>switchTab('by_id_style')} id="id-style-btn">By Interior Design Style</button>
    </div>

    <div class='tab-content'  class:active={activeTab==='by_id_style'} id="by_id_style">
        <form on:submit|preventDefault={suggest_by_style(selected_material_type,selected_style)}>
            <select bind:value={selected_material_type}>
                {#each material_types as mt}
                    <option value={mt}> {mt} </option>
                {/each}
            </select>
            
            <select bind:value={selected_style}>
                {#each interior_design_styles as style}
                    <option value={style}> {style} </option>
                {/each}
            </select>
            <button> Suggest </button>
        </form>
    
        {#if suggested_materials.length > 0}
            <div class="image-grid">
                {#each suggested_materials as m, i}
                    <label class="material-card" class:selected={selected_material_index===i}>
                        <input type=radio bind:group={selected_material_index} name="option" value={i} >
                        <MaterialCard material_name={m["name"]} material_path={m["filepath"]} material_info={m["reason"]} index={i}/>
                    </label>
                {/each}
            </div>
            <button on:click={()=>proceed_to_generate(suggested_materials[selected_material_index]["name"] + " " + selected_material_type)}> Generate Material Texture </button>
        {:else if is_loading==true}
            <div class="images-placeholder">
                <Circle size="60" color="#FF3E00" unit="px" duration="1s" />
            </div>
        {:else}
            <div class="images-placeholder">
                <pre>No materials suggested yet.</pre>
            </div>
        {/if}
    </div>

    

<style>
    
    .image-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        grid-column-gap: 0.25rem;
        grid-row-gap: 0.25rem;
    }

    .image-grid input[type="radio"] {
        opacity: 0;
        position: fixed;
        width:0; 
    } 

    .material-card {
        display:flex; 
        flex-direction: column;
        justify-content: space-around;
        border: 1px solid black;
    }

    .material-card:hover {
        border: 3px solid grey;
    }

    .material-card.selected {
        border: 3px solid blue;
    }

    .material-card.selected:hover {
        border: 3px solid blue;
    }

    .tab-content {
		display: none;
	}
  
	.tab-content.active {
		display: flex;
        flex-direction: column;
        height: 100%;
        width:100%;
        padding: 5px;
	}

    .tab-btn {
        height:100%;
    }

	.tab-btn.active {
		background-color: rgb(89, 185, 218);
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


</style>
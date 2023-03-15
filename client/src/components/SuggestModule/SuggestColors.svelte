<script>
    import ColorPalette from "./ColorPalette.svelte";
    import { Circle } from 'svelte-loading-spinners';

    const interior_design_styles = ['Modern', 'Traditional', 'Contemporary', 'Industrial', 'Transitional', 'Rustic', 'Bohemian', 'Minimalist', 'Hollywood Regency', 'Scandinavian']

    let selected_choices = [];
    let selected_style;

    let suggested_color_palettes=[];
    let selected_color_palettes=[];

    let selected_cp_index;

    let activeTab = 'by_id_style';
    function switchTab(tab) {
        activeTab = tab;
    }

    let is_loading=false;

    async function suggest_by_style(style){

        is_loading=true;

        let color_suggest_dict = {
            "style":style,
        }
        suggested_color_palettes=[];

        const color_suggestions_response = await fetch("/suggest_colors_by_style", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(color_suggest_dict),
        });
        const color_suggestions_json = await color_suggestions_response.json();
        suggested_color_palettes = await color_suggestions_json;
        console.log(suggested_color_palettes);
        is_loading=false;
        
    }

    function proceed_to_generate(material_name) {

    }

</script>
    <h4>Suggest Colors</h4>

    <div class="w3-bar w3-grey tabs">
        <button class='w3-bar-item w3-button tab-btn' class:active={activeTab==='by_id_style'} on:click={()=>switchTab('by_id_style')} id="id-style-btn">By Interior Design Style</button>
    </div>

    <div class='tab-content'  class:active={activeTab==='by_id_style'} id="by_id_style">
        <form on:submit|preventDefault={suggest_by_style(selected_style)}>
            <select bind:value={selected_style}>
                {#each interior_design_styles as style}
                    <option value={style}> {style} </option>
                {/each}
            </select>
            <button> Suggest Colors </button>
        </form>

        {#if suggested_color_palettes.length > 0}
            
            {#each suggested_color_palettes as cp}
                <div class="color-card">
                    <ColorPalette color_codes={cp["palette"]} name={cp["name"]} />
                </div>
            {/each}
            
        {:else if is_loading==true}
            <div class="images-placeholder">
                <Circle size="60" color="#FF3E00" unit="px" duration="1s" />
            </div>
        {:else}
            <div class="images-placeholder">
                <pre>No color palettes suggested yet.</pre>
            </div>
        {/if}
    </div> 

    

    


<style>
    

    .image-grid input[type="radio"] {
        opacity: 0;
        position: fixed;
        width:0; 
    } 

    .color-card {
        border: 1px solid black;
        padding: 5px;
        height: 100%;
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
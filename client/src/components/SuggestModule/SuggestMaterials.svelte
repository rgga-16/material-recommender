<script>
    import MaterialCard from "./MaterialCard.svelte";
    import ColorPalette from "./ColorPalette.svelte";

    const material_types = ["All types","wood","metal","fabric","ceramic"]
    const interior_design_styles = ['Modern', 'Traditional', 'Contemporary', 'Industrial', 'Transitional', 'Rustic', 'Bohemian', 'Minimalist', 'Hollywood Regency', 'Scandinavian']
    const suggestion_choices = ["Materials", "Colors"];

    let selected_choices = [];
    let selected_material_type;
    let selected_style;

    let do_suggest_materials=true;
    let do_suggest_colors=false; 

    let suggested_materials=[];
    let suggested_color_palettes=[];

    let selected_cp_index;
    let selected_material_index;

    async function suggest_by_style(material_type,style,suggest_materials,suggest_colors){

        if (suggest_materials===false && suggest_colors===false) {
            alert("Please choose to suggest at least either materials or colors.");
            return;
        }

        if(suggest_materials) {
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
        }

        if(suggest_colors) {

            let color_suggest_dict = {
                "style":style,
                "material_type":material_type
            }
            suggested_color_palettes=[];

            const color_suggestions_response = await fetch("/suggest_colors_by_style", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(color_suggest_dict),
            });
            const color_suggestions_json = await color_suggestions_response.json();
            suggested_color_palettes = await color_suggestions_json;
        }

    }

    function proceed_to_generate(material_name) {

    }

</script>

    <h4>Suggest Materials</h4>

    <form on:submit|preventDefault={suggest_by_style(selected_material_type,selected_style,do_suggest_materials,do_suggest_colors)}>
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

        <!-- <div class="checkbox-group">
            <label> 
                <input type=checkbox bind:checked={do_suggest_materials} value="Materials">
                Materials
            </label>
            
            <label> 
                <input type=checkbox bind:checked={do_suggest_colors} value="Colors">
                Colors
            </label> 

        </div>-->

        <button> Suggest </button>


    </form>
    {#if do_suggest_materials}
        {#await suggested_materials}
            <p>Loading material suggestions</p>
        {:then suggested_materials} 
            {#if suggested_materials.length > 0}
                <div class="image-grid">
                    {#each suggested_materials as m, i}
                        <label class="material-card" class:selected={selected_material_index===i}>
                            <input type=radio bind:group={selected_material_index} name="option" value={i} >
                            <MaterialCard material_name={m["name"]} material_path={m["filepath"]} material_info={m["reason"]} index={i}/>
                            <!-- <button> Proceed to generate </button> -->
                        </label>
                    {/each}
                </div>
            {:else}
                <p> Suggesting materials...</p>
            {/if}
        {/await}
        
    {/if}

    {#if do_suggest_colors}
        {#await suggested_color_palettes}
            <pre>Loading color suggestions</pre>
        {:then suggested_color_palettes} 
            {#if suggested_color_palettes.length > 0}
                <div class="image-grid">
                    {#each suggested_color_palettes as cp}
                        <div class="material-card">
                            <ColorPalette color_codes={cp["palette"]} name={cp["name"]} />
                        </div>
                    {/each}
                </div>
            {/if}
        {/await}
    {/if}


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

    /* .material-card:hover {
        border: 1px solid grey;
    }

    .material-card.selected {
        border: 1px solid blue;
    } */

</style>
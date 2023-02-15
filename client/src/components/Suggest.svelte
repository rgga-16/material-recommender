<script>

    const material_types = ["All types","wood","metal","fabric","ceramic"]
    const interior_design_styles = ['Modern', 'Traditional', 'Contemporary', 'Industrial', 'Transitional', 'Rustic', 'Bohemian', 'Minimalist', 'Hollywood Regency', 'Scandinavian']
    const suggestion_choices = ["Materials", "Colors"];

    let selected_choices = [];
    let selected_material_type;
    let selected_style;

    let do_suggest_materials=false;
    let do_suggest_colors=false; 

    let suggested_materials=[];
    let suggested_color_palettes=[];

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

            const material_suggestions_response = await fetch("/suggest_materials_by_style", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(material_suggest_dict),
            });
            const material_suggestions_json = await material_suggestions_response.json();
            suggested_materials = await material_suggestions_json["suggested_materials"];
        }

        if(suggest_colors) {

            let color_suggest_dict = {
                "style":style,
                "material_type":material_type
            }

            const color_suggestions_response = await fetch("/suggest_colors_by_style", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(color_suggest_dict),
            });
            const color_suggestions_json = await color_suggestions_response.json();
            suggested_color_palettes = await color_suggestions_json["suggested_color_palettes"];
        }

    }

</script>
    <h2>Material & Color Suggestion</h2>

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

        <div class="checkbox-group">
            <label> 
                <input type=checkbox bind:checked={do_suggest_materials} value="Materials">
                Materials
            </label>
            
            <label> 
                <input type=checkbox bind:checked={do_suggest_colors} value="Colors">
                Colors
            </label>

        </div>

        <button> Suggest </button>


    </form>
    {#if do_suggest_materials}
        {#await suggested_materials}
            <pre>Loading material suggestions</pre>
        {:then data} 
            {suggested_materials}
        {/await}
        
    {/if}

    {#if do_suggest_colors}
        {#await suggested_color_palettes}
            <pre>Loading color suggestions</pre>
        {:then data} 
            {suggested_color_palettes}
        {/await}
    {/if}


<style>

</style>
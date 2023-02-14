<script>

    const material_types = ["All types","wood","metal","fabric","ceramic"]
    const interior_design_styles = ['Modern', 'Traditional', 'Contemporary', 'Industrial', 'Transitional', 'Rustic', 'Bohemian', 'Minimalist', 'Hollywood Regency', 'Scandinavian']
    const suggestion_choices = ["Materials", "Colors"];

    let selected_choices = [];
    let selected_material_type;
    let selected_style;

    async function get_suggestion(){

    }

</script>
    <h2>Material & Color Suggestion</h2>

    <form on:submit|preventDefault={get_suggestion}>
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
            {#each suggestion_choices as choice}  
                <label> 
                    <input type=checkbox bind:group={selected_choices} value={choice}>
                    {choice}
                </label>
            {/each}
        </div>

        <button> Suggest </button>


    </form>


<style>

</style>
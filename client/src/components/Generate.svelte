<script>
    import {onMount} from 'svelte';
  import { loop_guard } from 'svelte/internal';

    let input_material='';
    let object_data={}; //List of names of 3D objects 

    let promise = fetch('./get_objects_and_parts').then((x)=>x.json());
    
 
</script>

<div class="material_generator">
    <h2> Material Generator </h2>
    <form>
        <input name="material_name" type="text" bind:value={input_material}/>
        
        <!-- WIP: Block for getting tabs of checkbox groups -->
        {#await promise}
            <pre>Loading</pre>
        {:then data} 
            {
            data.nightstand.parts.names[0]
            }
        {/await}
    
    </form>

</div>

<style>

</style>
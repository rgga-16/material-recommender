<script>
    export let obj; 
    export let object_info; 

    export let child_part; 
    export let parent_part; 

    async function get_assembly_feedback() {

    }


</script>

<div class="pairs">
    <div class="child-component">
        <p> <b> {child_part} </b></p>
        <img src={object_info[child_part]["mat_image_texture"]} alt={object_info[child_part]["mat_name"]} />
        <p> Material: {object_info[child_part]["mat_name"]}</p>
    </div>
    <p> ==> </p>
    <div class="parent-component">
        <p> <b> {parent_part} </b></p>
        <img src={object_info[parent_part]["mat_image_texture"]} alt={object_info[parent_part]["mat_name"]} />
        <p> Material: {object_info[parent_part]["mat_name"]}</p>
    </div>
</div>




<style>

</style>
<script>

    import * as THREE from 'three';
    import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
    import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
    import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';
    import { TextureLoader } from 'three/src/loaders/TextureLoader.js';

    import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';


    import { spring } from 'svelte/motion'
    import {curr_rendering_path} from '../stores.js';
	import {curr_texture_parts} from '../stores.js';
	import {curr_textureparts_path} from '../stores.js';

    import {selected_part_name} from '../stores.js'; 
    import {selected_obj_name} from '../stores.js';


    import { onMount, createEventDispatcher} from 'svelte';
    
    export let information_panel;

    let camera, scene, renderer, controls, raycaster;


    const gltfLoader = new GLTFLoader();



    const url = 'models/glb';
    let objs_and_parts = {}; //Dictionary of objects and their parts
    
    /**
     * part_infos = [
     *  {
     *      "name":"bedframe",
     *      "parent":"bed",
     *      "glb_url":"models/glb/bed/bedframe.glb"
     *  }....
     * 
     * ]
     */
    let part_infos = []; //List of all parts loaded from objs_and_parts including their parent object
    
    // let glbUrls = [];

    // let objects=[]; //List of all 3D models loaded from glb_url in part_infos. This is what we will be displaying in the 3D view.
    

    async function get_objects() {
        const obj_resp= await fetch('./get_objects_and_parts');
        const obj_json = await obj_resp.json(); 
        objs_and_parts = obj_json;

        for (const obj in objs_and_parts) {
            let o = objs_and_parts[obj];

            for (const part of o["parts"]["names"]) {

                part_infos.push({
                    "name":part,
                    "parent":obj,
                    "glb_url":url+'/'+obj+'/'+part+'.glb'
                });
                part_infos=part_infos;
                // glbUrls.push(url+'/'+obj+'/'+part+'.glb');
                // glbUrls=glbUrls;
            }
        }
        console.log(part_infos);
    }

    

    const highlightMaterial = new THREE.MeshBasicMaterial({
        color:0x0000ff,
        emissive: 0x0000ff,
        transparent:true,
        opacity: 0.5
    });


    let highlightedPart = null;
    let originalMaterial= null

    function onClick(event) {
        event.preventDefault();

        if (highlightedPart) {
            // console.log(highlightedPart);
            // alert('You clicked on the highlighted part: ' + highlightedPart.name);
            selected_part_name.set(highlightedPart.name);
            selected_obj_name.set(highlightedPart.parent);
            information_panel.displayTexturePart();

            /**
             * TODO: When I click on a highlighted object, I should be able to display the following to the Information Panel:
             * 1) Name of the object part that's highlighted (ex. blanket). ok 
             * 2) Name of the bigger object it is a part of (ex. bed). ok 
             * 3) The material used in that part (access this in the curr_texture_parts dict using the object name and part name)
             * 4) The finish used in that part (access this in the curr_rendering dict using the object name and part name)
             * 5) The color finish used in that part (access this in the curr_rendering dict using the object name and part name)
            */
        }

        
    }

    function onMouseMove(event) {
        const mouse = new THREE.Vector2(
            (event.clientX / window.innerWidth) * 2 - 1,
            -(event.clientY / window.innerHeight) * 2 + 1
        );

        raycaster.setFromCamera(mouse, camera);

        let objects = part_infos.map(item => item.model);
        const intersects = raycaster.intersectObjects(objects, true);

        if (intersects.length > 0) {
            const object = intersects[0].object;
            if (object !== highlightedPart) {
                if (highlightedPart) {
                    // highlightedPart.material = originalMaterial;
                    highlightedPart.model.children[0].material=originalMaterial;
                }
                const index = part_infos.findIndex(item => item.model.children[0] == object); //ASSUME that the first child of the model is the mesh

                // highlightedPart = object;
                highlightedPart = part_infos[index];
                originalMaterial = object.material;
                highlightedPart.model.children[0].material = highlightMaterial;
                // object.material = highlightMaterial;

                // console.log('Intersected object: ' + object);
                // console.log(object);
                // console.log('Original index: ' + index);

                

            }
        } else {
            if (highlightedPart) {
                // highlightedPart.material = originalMaterial;
                highlightedPart.model.children[0].material=originalMaterial;
                highlightedPart = null;
            }
        }

    }

    // const textureAlternative= textureUrls[1];

    
    function add_glb_objects() {


        for (let i = 0; i < part_infos.length; i++) {
            let glbUrl = part_infos[i]["glb_url"];
            gltfLoader.load(glbUrl, (gltf) => {
                // console.log('GLTF loaded: ' + gltf);
                let model = gltf.scene
                scene.add(model);
                part_infos[i]["model"] = model;
                part_infos=part_infos;
            })
        }
        console.log(part_infos);
    }

    function changeTexture(object, url) {
        object.traverse((node) => {
                if (node.isMesh) {
                    console.log("material changed")
                    const material = node.material;
                    if (Array.isArray(material)) {
                        material.forEach((mat) => {
                        mat.map = new THREE.TextureLoader().load(textureAlternative);
                        mat.needsUpdate = true;
                        });
                    } else {
                        material.map = new THREE.TextureLoader().load(textureAlternative);
                        material.needsUpdate = true;
                    }
                }
        });
    }


    function init() {
        renderer = new THREE.WebGLRenderer({ alpha: true });
        renderer.setSize( window.innerWidth/2, window.innerHeight/2); 
        
        const container = document.getElementById("3d-viewer");
        container.appendChild( renderer.domElement );

        scene = new THREE.Scene();
        scene.background = new THREE.Color(0x000000); // Set the background to black
        camera = new THREE.PerspectiveCamera( 75, window.innerWidth/window.innerHeight, 0.1, 1000 );
        
        
        raycaster = new THREE.Raycaster();
        renderer.domElement.addEventListener('mousemove', onMouseMove);
        renderer.domElement.addEventListener('click', onClick);


        // add_objects();
        add_glb_objects();

        const light = new THREE.AmbientLight(0xffffff, 0.4);
        scene.add(light);

        const environment = new RoomEnvironment();
        const pmremGenerator = new THREE.PMREMGenerator( renderer );

        scene.background = new THREE.Color( 0xbbbbbb );
        scene.environment = pmremGenerator.fromScene( environment ).texture;

        controls = new OrbitControls( camera, renderer.domElement );
        controls.enableDamping = true;
        controls.minDistance = 1;
        controls.maxDistance = 10;
        controls.target.set( 0, 0.35, 0 );
        controls.update();


        camera.position.z = 5;



    }

    

    onMount(async () => {
        await get_objects();
        init();

        function animate() {
            requestAnimationFrame( animate );
            controls.update(); // required if damping enabled
            renderer.render( scene, camera );
        }

        animate();
    });


</script>

<div id="3d-viewer"></div>

<div>
    <!-- <input type="text" bind:value={texturePath} placeholder="Enter image texture path" /> -->
    <button on:click|preventDefault={() => changeTexture(obj,textureAlternative)}>Change Texture</button>
</div>

<style>

    #3d-viewer {
        width: 100%;
        height: 100%;
    }

</style>

<!-- 
DUMP

<script> 


    const objLoader = new OBJLoader();
    const textureLoader = new TextureLoader();

    const objUrls = [
        'models/bedframe.obj',
        'models/blanket.obj',
        'models/mattress.obj'
    ]

    const textureUrls = [
        'models/wood.png',
        'models/fabric_blanket.png',
        'models/fabric_mattress.png'
    ]


    function add_objects() {
        for (let i=0; i < objUrls.length; i++) {
            let objUrl = objUrls[i];
            let textureUrl = textureUrls[i];

            objLoader.load(objUrl, (obj) => { 
                console.log('OBJ loaded: ' + obj);
                console.log(obj);

                textureLoader.load(textureUrl, (texture)=> {
                    console.log('Texture loaded: ' + texture);
                    obj.traverse( (child) => { 
                        if (child instanceof THREE.Mesh) {
                            console.log('Found mesh: ' + child);
                            console.log(texture);
                            child.material.map = texture;
                            child.material.needsUpdate = true;
                        }
                    });
                    scene.add(obj);
                })
            })
        }
    }



</script>



-->
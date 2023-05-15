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
    import { onMount, createEventDispatcher} from 'svelte';
    const dispatch = createEventDispatcher();

    let camera, scene, renderer, controls;

    const objLoader = new OBJLoader();
    const textureLoader = new TextureLoader();
    const gltfLoader = new GLTFLoader();
    const objects=[];

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

    const glbUrls = [
        'models/glb/floor.glb'
    ]
    const textureAlternative= textureUrls[1];

    let obj;

    function add_glb_objects() {
        for (let i = 0; i < glbUrls.length; i++) {
            let glbUrl = glbUrls[i];
            gltfLoader.load(glbUrl, (gltf) => {
                console.log('GLTF loaded: ' + gltf);
                console.log(gltf);
                let model = gltf.scene
                scene.add(model);
                obj = model;
            })
        }
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

    function init() {
        renderer = new THREE.WebGLRenderer({ alpha: true });
        renderer.setSize( window.innerWidth/2, window.innerHeight/2); 
        
        const container = document.getElementById("3d-viewer");
        container.appendChild( renderer.domElement );

        scene = new THREE.Scene();
        scene.background = new THREE.Color(0x000000); // Set the background to black
        camera = new THREE.PerspectiveCamera( 75, window.innerWidth/window.innerHeight, 0.1, 1000 );



        // add_objects();
        add_glb_objects();

        const light = new THREE.AmbientLight(0xffffff, 0.7);
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



    onMount(() => {

        init();
        
        
        // document.body.appendChild( renderer.domElement );

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
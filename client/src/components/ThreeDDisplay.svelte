<script>

    import * as THREE from 'three';
    import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
    import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
    import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

    import {get} from 'svelte/store';

    import {curr_rendering_path} from '../stores.js';
	import {curr_texture_parts} from '../stores.js';
	import {curr_textureparts_path} from '../stores.js';

    import {isDraggingImage} from '../stores.js';
    import {generated_texture_name} from '../stores.js';

    // import {selected_part_name} from '../stores.js'; 
    // import {selected_obj_name} from '../stores.js';
    import {selected_objs_and_parts} from '../stores.js';
    import {objects_3d} from '../stores.js';

    import {transferred_texture_url} from '../stores.js';
    import {transferred_textureimg_url} from '../stores.js';
    import {transferred_texture_name} from '../stores.js';
    

    import {displayWidth} from '../stores.js';
    import {displayHeight} from '../stores.js';

    import { onMount } from 'svelte';
    
    export let information_panel;

    export let current_texture_parts;

    let width;
    let height; 
    const widthOffset = 25;
    const heightOffset = 95;

    /**
     * model3d_infos = [
     *  {
     *      "name":"bedframe",
     *      "parent":"bed",
     *      "glb_url":"models/glb/bed/bedframe.glb"
     *  }....
     * 
     * ]
     */
    let model3d_infos = []; //List of all 3D models laoded from current_texture_parts including their parent object

    export function update_3d_scene() {
        selected_objs_and_parts.set([]);
        SELECTED_INFOS=[];
        model3d_infos=[];
        current_texture_parts=get(curr_texture_parts);
        get_models();
        setup_scene();
        information_panel.displayTexturePart();
        
    }

    displayWidth.subscribe(value => {
        width = value - widthOffset;
    });

    displayHeight.subscribe(value => {
        height = value - heightOffset;
    });

    selected_objs_and_parts.subscribe(value => {
        // console.log(get(objects_3d));
        // console.log("selected_objs_and_parts changed");
        // console.log(value);
        // console.log("objs and parts");

        // objects_3d.set(model3d_infos);
        // console.log(get(objects_3d));
        /**
         * Basically, if  the selected_objs_and_parts (selected 3D models) have been modified, it will also be reflected in
         * objs_and_parts (all 3D models). So, there's no need to manually update (I think?)
        */
    });


    let camera, scene, renderer, controls, raycaster;
    const pointer = new THREE.Vector2();

    const gltfLoader = new GLTFLoader();
    // gltfLoader.setMeshoptDecoder(THREE.MeshoptDecoder); // Set meshoptDecoder to THREE.MeshoptDecoder

    let dragging = false;
    isDraggingImage.subscribe(value => {
        dragging = value;
    });
    
    let dragged_texture_url = null;
    transferred_texture_url.subscribe(value=> {
        // console.log("transferred_texture_url changed");
        dragged_texture_url = value;
    });

    let dragged_textureimg_url = null;
    transferred_textureimg_url.subscribe(value=> {
        // console.log("transferred_textureimg_url changed");
        dragged_textureimg_url = value;
    });

    let dragged_texture_name = null;
    transferred_texture_name.subscribe(value=> {
        // console.log("transferred_texture_name changed");
        dragged_texture_name = value;
    });

    function get_models() {
        model3d_infos = [];
        for(let obj in current_texture_parts) {
            for(let part in current_texture_parts[obj]) {
                model3d_infos.push( {
                    "name":part,
                    "parent":obj,
                    "glb_url": current_texture_parts[obj][part]["model"],
                    "is_selectable": current_texture_parts[obj][part]["is_selectable"]
                })
                model3d_infos=model3d_infos
            }
        }
        objects_3d.set(model3d_infos);
    }

    let HIGHLIGHTED; 
    let SELECTED_INFOS = [];
    $: SELECTEDS = SELECTED_INFOS.map(item => item.model.children[0]);

    let mouseDown=false;
    let shiftPressed=false;

    export function removeHighlights() {
        if(HIGHLIGHTED) {
            HIGHLIGHTED.material.emissive.setHex(0x000000);
            HIGHLIGHTED=null;
        }

        if (SELECTEDS.length > 0) {
                for (let i = 0; i < SELECTEDS.length; i++) {
                    SELECTEDS[i].material.emissive.setHex(0x000000);
                }
                SELECTEDS = [];
                SELECTED_INFOS = [];
                selected_objs_and_parts.set(SELECTED_INFOS);
        }
    }

    async function moveTextureMap(src_url) {
        const response = await fetch("/move_image", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                "src_url": src_url,
                "curr_textureparts_path": get(curr_textureparts_path),
            }),
        });

        const data = await response.json();
        const dest_url = await data["dest_url"];
        return dest_url;
    }

    function onPointerClick(event) {
        event.preventDefault();

        if(!isMouseOver3DScene(event)) {
            return;
        }
        raycaster.setFromCamera(pointer, camera);
        let objects = model3d_infos.map(item => item.model);
        const intersects = raycaster.intersectObjects(objects, true); 

        if (intersects.length > 0) {
            if(!(intersects.some(element => element ===undefined))) {
                const clicked_object = intersects[0].object; //This is the object clicked on. 
                const index = SELECTEDS.indexOf(clicked_object);
                if (index === -1) {//If clicked object hasn't been selected yet, select it.

                    if(isObjectSelectable(clicked_object)) {
                        if (shiftPressed) { //If shift is held, want to select multiple objects
                            SELECTEDS.push(clicked_object);
                            const index = model3d_infos.findIndex(item => item.name === clicked_object.model_name && item.parent === clicked_object.model_parent);
                            SELECTED_INFOS.push(model3d_infos[index]);
                            // console.log("Has not been selected yet. Appending it to selected objects.")
                            SELECTEDS=SELECTEDS;    
                            SELECTED_INFOS=SELECTED_INFOS;
                            selected_objs_and_parts.set(SELECTED_INFOS);
                            // console.log(get(selected_objs_and_parts));
                            information_panel.displayTexturePart();
                        } else { //If shift is not held, want to select only one object
                            SELECTEDS = [];
                            SELECTED_INFOS = [];
                            SELECTEDS[0] = clicked_object;
                            // console.log(clicked_object);
                            // console.log(model3d_infos);
                            // const index = model3d_infos.findIndex(item => item.model.children[0].name === clicked_object.model_name);
                            const index = model3d_infos.findIndex(item => item.name === clicked_object.model_name && item.parent === clicked_object.model_parent);
                            
                            // console.log(get(curr_texture_parts));
                            SELECTED_INFOS[0] = model3d_infos[index];
                            // console.log("Has not been selected yet. Selecting it.")

                            SELECTEDS=SELECTEDS;    
                            SELECTED_INFOS=SELECTED_INFOS;
                            selected_objs_and_parts.set(SELECTED_INFOS);
                            // console.log(get(selected_objs_and_parts));
                            information_panel.displayTexturePart();
                        }
                    } else {
                        if (SELECTEDS.length > 0) {
                            for (let i = 0; i < SELECTEDS.length; i++) {
                                SELECTEDS[i].material.emissive.setHex(0x000000);
                            }
                            SELECTEDS = [];
                            SELECTED_INFOS = [];
                            selected_objs_and_parts.set(SELECTED_INFOS);
                        }
                        // console.log("Nothing's been selected.")
                    }

                } else {//If clicked object has already been selected, deselect it. 
                    SELECTEDS[0].material.emissive.setHex(0x000000);
                    SELECTEDS.splice(index, 1);
                    SELECTED_INFOS.splice(index, 1);
                    // console.log("Has been selected. Deselected.")

                    SELECTEDS=SELECTEDS;    
                    SELECTED_INFOS=SELECTED_INFOS;
                    selected_objs_and_parts.set(SELECTED_INFOS);
                    information_panel.displayTexturePart();
                }
                SELECTEDS=SELECTEDS;    
                SELECTED_INFOS=SELECTED_INFOS;
                selected_objs_and_parts.set(SELECTED_INFOS);
                information_panel.displayTexturePart();
            }
        } else {// If the user clicks on an empty space, then we want to deselect the selected object.
            if (SELECTEDS.length > 0) {
                for (let i = 0; i < SELECTEDS.length; i++) {
                    SELECTEDS[i].material.emissive.setHex(0x000000);
                }
                SELECTEDS = [];
                SELECTED_INFOS = [];
                selected_objs_and_parts.set(SELECTED_INFOS);
            }
            // console.log("Nothing's been selected.")
        }
        // console.log(get(selected_objs_and_parts));
        // information_panel.displayTexturePart();
    }

    function getPointedObject() {
        raycaster.setFromCamera(pointer, camera);
        let objects = model3d_infos.map(item => item.model);
        const intersects = raycaster.intersectObjects(objects, true); //intersects is a list of objects pointed by the mouse
        if (intersects.length > 0) { //if intersects has elements 
            if (!(intersects.some(element => element===undefined))) { //if intersects does not have undefined elements
                return intersects[0].object;
            } else {
                return null;
            }
        }
    }

    function isObjectSelectable(object) {
        const index = model3d_infos.findIndex(item => item.name === object.model_name && item.parent === object.model_parent);
        const model3d_info = model3d_infos[index];
        let is_selectable = false;

        if(model3d_info) {
            if(model3d_info.is_selectable) {
                is_selectable = true;
            } else {
                is_selectable = false;
            }
        }

        return is_selectable;

    }

    function highlightObject() {
        if(SELECTEDS.length > 0) {
            for (const selected of SELECTEDS) {
                selected.material.emissive.setRGB(0,0,1);
                selected.material.emissiveIntensity=0.2;
            }
        }
        const object = getPointedObject();


        if(object) {
            //HIGHLIGHTED is the object that is highlighted in red
                //if there was already highlighted object is not the same as the one pointed by the mouse
            if (HIGHLIGHTED != object) {
                if (HIGHLIGHTED) {  //if there is a highlighted object
                    //reset the color of the highlighted object
                    HIGHLIGHTED.material.emissive.setRGB(0,0,0);
                    HIGHLIGHTED.material.emissiveIntensity=0;
                }

                if(isObjectSelectable(object)) {
                    HIGHLIGHTED = object; //set the highlighted object to the one pointed by the mouse
                    HIGHLIGHTED.currentHex = HIGHLIGHTED.material.emissive.getHex();//save the color of object before it is highlighted
                    HIGHLIGHTED.material.emissive.setRGB(1,0,0);
                    HIGHLIGHTED.material.emissiveIntensity=0.2;
                } else {
                    HIGHLIGHTED = null;
                    // HIGHLIGHTED.material.emissive.setRGB(0,0,0);
                    // HIGHLIGHTED.material.emissiveIntensity=0;
                }
                
            }
        } else {
            if (HIGHLIGHTED) {
                // HIGHLIGHTED.material.emissive.setHex(0x000000);//reset the color of the highlighted object
                HIGHLIGHTED.material.emissive.setRGB(0,0,0);
                HIGHLIGHTED.material.emissiveIntensity=0;
                HIGHLIGHTED = null;
            }
        }
    }

    function onWindowResize() {
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        renderer.setSize(width, height);
    }

    function isMouseOver3DScene(event) {
        const rect = renderer.domElement.getBoundingClientRect();
        return (event.clientX >= rect.left && event.clientX <= rect.right && event.clientY >= rect.top && event.clientY <= rect.bottom);
    }

    async function onPointerMove(event) {
        if (isMouseOver3DScene) {
            const rect = renderer.domElement.getBoundingClientRect();
            pointer.x = ((event.clientX-rect.left) / width) * 2 - 1;
            pointer.y = -((event.clientY-rect.top) / height) * 2 + 1;

            if (mouseDown) {
                if(dragging) {
                    if (dragged_texture_url) {
                        if(SELECTEDS.length > 0) {
                            for (let selected of SELECTEDS) {
                                const index = SELECTED_INFOS.findIndex(item => item.name === selected.model_name && item.parent === selected.model_parent);

                                let SELECTED_INFO = SELECTED_INFOS[index];
                                let selected_object_name = SELECTED_INFO.name;
                                let selected_parent_object = SELECTED_INFO.parent;
                                
                                let cloned_texture_parts = get(curr_texture_parts);

                                let prev_texture_parts = Object.assign( {}, cloned_texture_parts); 
                                // console.log("BEFORE");
                                // console.log(prev_texture_parts);

                                selected = changeTexture(selected,dragged_texture_url);

                                let dest_url = await moveTextureMap(dragged_textureimg_url);

                                cloned_texture_parts[selected_parent_object][selected_object_name]["mat_name"] = dragged_texture_name;
                                // cloned_texture_parts[selected_parent_object][selected_object_name]["mat_image_texture"] = dragged_textureimg_url;
                                cloned_texture_parts[selected_parent_object][selected_object_name]["mat_image_texture"] = dest_url;

                                curr_texture_parts.set(cloned_texture_parts);
                                
                                console.log("AFTER");    
                                console.log(get(curr_texture_parts));

                                console.log("SELECTED OBJECT");
                                console.log(selected);
                                const models3d_idx = model3d_infos.findIndex(item => item.name === selected_object_name && item.parent === selected_parent_object);
                                
                                console.log("The selected object in models3d");
                                console.log(model3d_infos[models3d_idx]);

                                console.log("The selectd object in objects_3d");
                                console.log(get(objects_3d)[models3d_idx]);

                                // Code for updating the objects_3d model with the model with the updated texture
                                model3d_infos[models3d_idx]['model']['children'][0] = selected;
                                objects_3d.set(model3d_infos);
                                console.log("UPDATED OBJECTS_3D");
                                console.log(get(objects_3d))

                                information_panel.displayTexturePart();
                            }
                            transferred_texture_name.set(null);
                            transferred_texture_url.set(null);
                            transferred_textureimg_url.set(null);
                            isDraggingImage.set(false);
                        } else {
                            transferred_texture_name.set(null);
                            transferred_texture_url.set(null);
                            transferred_textureimg_url.set(null);
                            isDraggingImage.set(false);
                            alert("No selected object. Please select an object first.");
                        }
                    }
                }

            }
        }

    }

    function onMouseDown(event) {
        if (event.button === 0) {
            mouseDown = true;

        }
    }

    function onMouseUp(event) {
        if(event.button===0) {
            mouseDown = false;

        }
    }

    
    function add_glb_objects() {
        for (let i = 0; i < model3d_infos.length; i++) {
            let glbUrl = model3d_infos[i]["glb_url"];
            gltfLoader.load(glbUrl, (gltf) => {
                // console.log('GLTF loaded: ' + gltf);
                let model = gltf.scene
                
                //Workaround. If the model.children[0] is Object3D, the Mesh is found in model.children[0].children[0]. 
                // Replace model.children[0] with model.children[0].children[0]
                if(model.children[0] instanceof THREE.Object3D && !(model.children[0] instanceof THREE.Mesh)) {
                    // console.log("model.children[0] is Object3D. Changing it to a Mesh.");
                    const real_mesh = model.children[0].children[0];
                    model.children[0] = real_mesh;
                }

                model.traverse(function(child) {
                    child.model_name = model3d_infos[i]["name"];
                    child.model_parent = model3d_infos[i]["parent"];    
                });

                scene.add(model);
                model3d_infos[i]["model"] = model;
                model3d_infos=model3d_infos;
            })
        }
        // console.log(model3d_infos);
    }

    function changeTexture(object, url) {
        console.log(object);

        object.traverse((node) => {
            console.log(node);
            if (node.isMesh) {
                // console.log("material changed");
                // console.log(node);
                const material = new THREE.MeshStandardMaterial();

                if (Array.isArray(material)) {
                    material.forEach((mat) => {
                        const texturemap = new THREE.TextureLoader().load(url);
                        texturemap.wrapS = THREE.RepeatWrapping;
                        texturemap.wrapT = THREE.RepeatWrapping;
                        var bbox = new THREE.Box3().setFromObject(object);
                        const size = new THREE.Vector3();
                        bbox.getSize(size);
                        const length = size.x;
                        const width = size.z; 
                        texturemap.repeat.set(length, width);
                        mat.map = texturemap;
                        mat.needsUpdate = true;
                        // mat.color=null;
                        mat.emissive.setRGB(0,0,0);
                        mat.emissiveIntensity=0;
                    });
                } else {
                    // BUG ( TypeError: Cannot read properties of null (reading 'toArray')) IS SOMEWHERE FUCKING HERE
                    const texturemap = new THREE.TextureLoader().load(url);
                    texturemap.wrapS = THREE.RepeatWrapping;
                    texturemap.wrapT = THREE.RepeatWrapping;
                    var bbox = new THREE.Box3().setFromObject(object);
                    const size = new THREE.Vector3();
                    bbox.getSize(size);
                    const length = size.x;
                    const width = size.z; 
                    texturemap.repeat.set(length, width);
                    material.map = texturemap;
                    material.needsUpdate = true;
                    // material.color=null; //The bug is here in this lil crap
                    material.emissive.setRGB(0,0,0);
                    material.emissiveIntensity=0;
                }
                node.material=material;
                node=node;
            }
        });
        console.log(object);
        object=object;
        return object;
    }

    function setup_scene() {
        while (scene.children.length > 0) {
            scene.remove(scene.children[0]);
        }
        add_glb_objects();
        const light = new THREE.AmbientLight(0xffffff, 0.1);
        scene.add(light);
    }

    function init() {
        const container = document.getElementById("3d-viewer");
        container.innerHTML = "";
        renderer = new THREE.WebGLRenderer({ alpha: true });
        // renderer.setSize( window.innerWidth/2, window.innerHeight/2); 
        renderer.setSize( width, height); 
        
        container.appendChild( renderer.domElement );

        scene = new THREE.Scene();
        scene.background = new THREE.Color(0x000000); // Set the background to black

        camera = new THREE.PerspectiveCamera( 70, width/height, 0.1, 10000 );
        
        raycaster = new THREE.Raycaster();

        window.addEventListener('mousedown', onMouseDown);
        window.addEventListener('mouseup', onMouseUp);
        window.addEventListener('mousemove', onPointerMove);
        window.addEventListener('resize', onWindowResize);
        window.addEventListener('keydown', function(event) {
            if (event.key === "Shift") { // 16 is the key code for the shift key
                shiftPressed = true;
                
            }
        });
            window.addEventListener('keyup', function(event) {
            if (event.key === "Shift") { // 16 is the key code for the shift key
                shiftPressed = false;
            }
        });
        renderer.domElement.addEventListener('click', onPointerClick);

        setup_scene();

        const environment = new RoomEnvironment();
        const pmremGenerator = new THREE.PMREMGenerator( renderer );

        scene.background = new THREE.Color( 0xbbbbbb );
        scene.environment = pmremGenerator.fromScene( environment ).texture;

        controls = new OrbitControls( camera, renderer.domElement );
        controls.mouseButtons = {
            LEFT: null,
            MIDDLE: THREE.MOUSE.PAN,
            RIGHT: THREE.MOUSE.ROTATE
        }

        controls.minDistance = 1;
        controls.maxDistance = 10;
        controls.target.set( 0, 0.35, 0 );
        controls.update();
        camera.position.z = 5;
    }

    

    onMount(async () => {
        // await get_objects();
        get_models();

        init();

        function render() {
            requestAnimationFrame( render );
            controls.update(); // required if damping enabled

            camera.updateMatrixWorld();

            highlightObject();

            renderer.render( scene, camera );
        }
        render();
    });

</script>

<div id="3d-viewer"></div>


<style>

    #3d-viewer {
        width: inherit;
        height: inherit;
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

    function onMouseMove(event) {

        const mouse = new THREE.Vector2(
            (event.clientX / width) * 2  - 1,
            -(event.clientY / height) *2   + 1
        );

        raycaster.setFromCamera(mouse, camera);

        let objects = model3d_infos.map(item => item.model);
        const intersects = raycaster.intersectObjects(objects, true);

        if (intersects.length > 0) {
            const object = intersects[0].object;
            if (object == selectedPart) {
                return; 
            }
            if (object !== highlightedPart) {
                if (highlightedPart) {
                    // highlightedPart.material = originalMaterial;
                    highlightedPart.model.children[0].material=originalMaterial;
                }
                const index = model3d_infos.findIndex(item => item.model.children[0] == object); //ASSUME that the first child of the model is the mesh

                // highlightedPart = object;
                highlightedPart = model3d_infos[index];
                originalMaterial = object.material;
                highlightedPart.model.children[0].material = highlightMaterial;
                // object.material = highlightMaterial;
            }
        } else {
            if (highlightedPart) {
                // highlightedPart.material = originalMaterial;
                highlightedPart.model.children[0].material=originalMaterial;
                highlightedPart = null;
            }
        }

        if (selectedPart && selectedPart !== highlightedPart) {
            selectedPart.model.children[0].material = selectedMaterial;
            // selectedPart = null;
        }

    }

    // onClick event if the user clicks anywhere on the 3D display.
    function onClick(event) {
        event.preventDefault();

        // If a selected part already exists, then we need to reset the material of the selected part
        if (selectedPart) {
            selectedPart.model.children[0].material = originalSelectedMaterial;
            selectedPart =null;
        }

        if (highlightedPart) { //If a highlighted part exists, then we need to set the selected part to the highlighted part
            selectedPart = highlightedPart;
            originalSelectedMaterial=originalMaterial;
            selectedPart.model.children[0].material = selectedMaterial;
            // console.log(highlightedPart);
            // alert('You clicked on the highlighted part: ' + highlightedPart.name);
            selected_part_name.set(selectedPart.name);
            selected_obj_name.set(selectedPart.parent);
            information_panel.displayTexturePart();

        } else {
            selectedPart.model.children[0].material = originalSelectedMaterial;
            highlightedPart = null;
            selectedPart = null; 
        }

        
    }




</script>



-->
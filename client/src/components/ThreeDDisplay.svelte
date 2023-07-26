<script>

    import * as THREE from 'three';
    import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
    import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
    import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';


    import {get} from 'svelte/store';

    import {curr_rendering_path} from '../stores.js';
	import {curr_texture_parts} from '../stores.js';
	import {curr_textureparts_path} from '../stores.js';
    import {action_history} from '../stores.js';
    import {addToHistory} from '../main.js';
    import {getImage} from '../main.js';
    import {degreeToRadians} from '../main.js';

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

    // curr_texture_parts.update(value => {
    //     current_texture_parts = value;  
    // });

    export function update_3d_scene() {
        selected_objs_and_parts.set([]);
        SELECTED_INFOS=[];
        model3d_infos=[];
        current_texture_parts=get(curr_texture_parts);
        get_models();
        setup_scene();
        //information_panel.displayTexturePart();
        
    }

    export async function fullTextureTransferAlgorithm() {

        if(SELECTEDS.length > 0) {
            for (let selected of SELECTEDS) {
                const index = SELECTED_INFOS.findIndex(item => item.name === selected.model_name && item.parent === selected.model_parent);

                let SELECTED_INFO = SELECTED_INFOS[index];
                let selected_object_name = SELECTED_INFO.name;
                let selected_parent_object = SELECTED_INFO.parent;
                
                let cloned_texture_parts = get(curr_texture_parts);

                const textureimg_url_noext = dragged_textureimg_url.split(".")[0];
                const ext = dragged_textureimg_url.split(".")[1];
                const texturenormal_url = textureimg_url_noext + "_normal." + ext;
                const textureheight_url = textureimg_url_noext + "_height." + ext;

                if (dragged_texture_name===null || dragged_texture_name===null) {
                    alert("Error in dragging and dropping texture. Please try again.");
                    return;
                }

                const old_mat_name = cloned_texture_parts[selected_parent_object][selected_object_name]["mat_name"];
                const old_mat_image_texture = cloned_texture_parts[selected_parent_object][selected_object_name]["mat_image_texture"];
                let old_mat_normal_texture = null;
                if ("mat_normal_texture" in cloned_texture_parts[selected_parent_object][selected_object_name]) {
                    old_mat_normal_texture = cloned_texture_parts[selected_parent_object][selected_object_name]["mat_normal_texture"];
                }
                let old_mat_height_texture = null;
                if ("mat_height_texture" in cloned_texture_parts[selected_parent_object][selected_object_name]) {
                    old_mat_height_texture = cloned_texture_parts[selected_parent_object][selected_object_name]["mat_height_texture"];
                }

                
                
                await transferTexture(selected_parent_object, selected_object_name, dragged_texture_name, dragged_textureimg_url, texturenormal_url, textureheight_url);
                
                addToHistory("Change Texture", 
                selected_parent_object, selected_object_name, 
                ["mat_name","mat_image_texture","mat_normal_texture",
                "mat_height_texture"], 
                [old_mat_name,old_mat_image_texture,old_mat_normal_texture,
                old_mat_height_texture], 
                [dragged_texture_name,dest_url,
                normalmap_texture_url,heightmap_texture_url]);
                
                curr_texture_parts.set(cloned_texture_parts);
                //information_panel.displayTexturePart();
            }
            dragging=false;
            dragged_texture_name=null;
            dragged_texture_url=null;
            dragged_textureimg_url=null;

            transferred_texture_name.set(null);
            transferred_texture_url.set(null);
            transferred_textureimg_url.set(null);
            isDraggingImage.set(false);
        } else {
            dragging=false;
            dragged_texture_name=null;
            dragged_texture_url=null;
            dragged_textureimg_url=null;

            transferred_texture_name.set(null);
            transferred_texture_url.set(null);
            transferred_textureimg_url.set(null);
            isDraggingImage.set(false);
            alert("No selected object. Please select an object first.");
        }
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

    let dest_url = null;
    let heightmap_texture_url = null;
    let normalmap_texture_url = null;

    let dragged_textureimg_url = null;
    transferred_textureimg_url.subscribe(value=> {
        // console.log("transferred_textureimg_url changed");
        dragged_textureimg_url = value;
    });

    let dragged_texture_name = null;
    transferred_texture_name.subscribe(value=> {
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

        for (let i = 0; i < model3d_infos.length; i++) {
            model3d_infos[i].model.children[0].material.emissive.setHex(0x000000);
        }
    }

    function removeHighlightsFromUnselecteds() {
        for (let i = 0; i < model3d_infos.length; i++) {
            if(!SELECTED_INFOS.includes(model3d_infos[i])) {
                model3d_infos[i].model.children[0].material.emissive.setHex(0x000000);
            }
        }
    }

    async function moveTextureMap(src_url) {
        // console.log("SOURCE URL: " + src_url);
        const response = await fetch("/transfer_texture", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                "src_url": src_url,
                "curr_textureparts_path": get(curr_textureparts_path),
                "curr_textureparts": get(curr_texture_parts),
            }),
        });

        const data = await response.json();
        dest_url = await data["img_url"];
        normalmap_texture_url = await data["normal_url"];
        heightmap_texture_url = await data["height_url"];
        console.log("dest_url: " + dest_url);
        console.log("normal_url: " + normalmap_texture_url);
        console.log("height_url: " + heightmap_texture_url);
        // return dest_url, normalmap_texture_url, heightmap_texture_url;
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
                console.log(clicked_object);
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
                            // //information_panel.clearTexturePart();
                        } else { //If shift is not held, want to select only one object
                            SELECTEDS = [];
                            SELECTED_INFOS = [];
                            SELECTEDS[0] = clicked_object;
                            // console.log(clicked_object);
                            // console.log(model3d_infos);
                            const index = model3d_infos.findIndex(item => item.name === clicked_object.model_name && item.parent === clicked_object.model_parent);
                            // console.log(get(curr_texture_parts));
                            SELECTED_INFOS[0] = model3d_infos[index];
                            // console.log("Has not been selected yet. Selecting it.")
                            SELECTEDS=SELECTEDS;    
                            SELECTED_INFOS=SELECTED_INFOS;
                            selected_objs_and_parts.set(SELECTED_INFOS);
                            //information_panel.clearTexturePart();
                        }
                    } else {
                        if (SELECTEDS.length > 0) {
                            for (let i = 0; i < SELECTEDS.length; i++) {
                                SELECTEDS[i].material.emissive.setHex(0x000000);
                            }
                            SELECTEDS = [];
                            SELECTED_INFOS = [];
                            selected_objs_and_parts.set(SELECTED_INFOS);
                            removeHighlightsFromUnselecteds();
                        }
                    }
                } else {//If clicked object has already been selected, deselect it. 
                    SELECTEDS[0].material.emissive.setHex(0x000000);
                    SELECTEDS.splice(index, 1);
                    SELECTED_INFOS.splice(index, 1);
                    // console.log("Has been selected. Deselected.")
                    SELECTEDS=SELECTEDS;    
                    SELECTED_INFOS=SELECTED_INFOS;
                    selected_objs_and_parts.set(SELECTED_INFOS);
                    information_panel.clearTexturePart();
                    removeHighlightsFromUnselecteds();
                }
                SELECTEDS=SELECTEDS;    
                SELECTED_INFOS=SELECTED_INFOS;
                selected_objs_and_parts.set(SELECTED_INFOS);
                // //information_panel.clearTexturePart();
            }
        } else {// If the user clicks on an empty space, then we want to deselect the selected object.
            if (SELECTEDS.length > 0) {
                information_panel.clearTexturePart();
                for (let i = 0; i < SELECTEDS.length; i++) {
                    SELECTEDS[i].material.emissive.setHex(0x000000);
                }
                SELECTEDS = [];
                SELECTED_INFOS = [];
                selected_objs_and_parts.set(SELECTED_INFOS);
                removeHighlightsFromUnselecteds();
            }
            // console.log("Nothing's been selected."
        }
        // //information_panel.clearTexturePart();
        removeHighlightsFromUnselecteds();
    }

    function getPointedObject() {
        raycaster.setFromCamera(pointer, camera);
        let objects = model3d_infos.map(item => item.model);
        
        // BUG: caught TypeError: Cannot read properties of undefined (reading 'layers') */
        let intersects; 
        try {
            intersects = raycaster.intersectObjects(objects, true); //intersects is a list of objects pointed by the mouse
        } catch (error) {
            console.log(error);
            intersects = [];
        }

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

    // WIP
    export async function transferTexture(object_name, part_name, mat_name, image_path,normal_path,height_path) {
        let cloned_texture_parts = get(curr_texture_parts);
        const index = model3d_infos.findIndex(item => item.name === part_name && item.parent === object_name);
        if(index === -1) {
            console.error("Error: Could not find the object in the model3d_infos array.");
            alert("Error: Could not find the object in the model3d_infos array.");
            return;
        }
        let model = model3d_infos[index]['model']['children'][0];

        //Code to convert normal_url and height_url to blob
        let normal_mat_blob = await getImage(normal_path);
        let height_mat_blob= await getImage(height_path);
        let img_mat_blob = await getImage(image_path);

        let color = cloned_texture_parts[object_name][part_name]['color'] ? cloned_texture_parts[object_name][part_name]['color'] : "#FFFFFF"; 
        let opacity = cloned_texture_parts[object_name][part_name]['opacity'] ? cloned_texture_parts[object_name][part_name]['opacity'] : 1;
        let roughness = cloned_texture_parts[object_name][part_name]['roughness'] ? cloned_texture_parts[object_name][part_name]['roughness'] : 0.5;
        let metalness = cloned_texture_parts[object_name][part_name]['metalness'] ? cloned_texture_parts[object_name][part_name]['metalness'] : 0.0;
        let translationX = cloned_texture_parts[object_name][part_name]['offsetX'] ? cloned_texture_parts[object_name][part_name]['offsetX'] : 0;
        let translationY = cloned_texture_parts[object_name][part_name]['offsetY'] ? cloned_texture_parts[object_name][part_name]['offsetY'] : 0;
        let rotation = cloned_texture_parts[object_name][part_name]['rotation'] ? cloned_texture_parts[object_name][part_name]['rotation'] : 0;
        let scaleX = cloned_texture_parts[object_name][part_name]['scaleX'] ? cloned_texture_parts[object_name][part_name]['scaleX'] : 1;
        let scaleY = cloned_texture_parts[object_name][part_name]['scaleY'] ? cloned_texture_parts[object_name][part_name]['scaleY'] : 1;
        let normalScale =cloned_texture_parts[object_name][part_name]['normalScale']  ? cloned_texture_parts[object_name][part_name]['normalScale'] : 0.0;

        model = changeTexture(model,img_mat_blob, normal_mat_blob,height_mat_blob,
        color,opacity,roughness,metalness,translationX,translationY,rotation,scaleX,scaleY,normalScale);

        // This function moves the file location of the texture map to the current directory
        await moveTextureMap(image_path);

        model3d_infos[index]['model']['children'][0] = model;
        objects_3d.set(model3d_infos);

        cloned_texture_parts[object_name][part_name]["mat_name"] = mat_name;
        cloned_texture_parts[object_name][part_name]["mat_image_texture"] = dest_url;
        cloned_texture_parts[object_name][part_name]["mat_normal_texture"] = normalmap_texture_url;
        cloned_texture_parts[object_name][part_name]["mat_height_texture"] = heightmap_texture_url;

        curr_texture_parts.set(cloned_texture_parts);
    }

    async function onPointerMove(event) {
        if (isMouseOver3DScene) {
            const rect = renderer.domElement.getBoundingClientRect();
            pointer.x = ((event.clientX-rect.left) / width) * 2 - 1;
            pointer.y = -((event.clientY-rect.top) / height) * 2 + 1;

            if (mouseDown) {
                if(dragging) {
                    if (dragged_texture_url && dragged_textureimg_url && dragged_texture_name) { 
                        fullTextureTransferAlgorithm();

                    
                    }
                }

            }
        } else {
            alert("improperly dragged");
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
                    if(current_texture_parts[model3d_infos[i]["parent"]][model3d_infos[i]["name"]]["color"]) {
                        const color = current_texture_parts[model3d_infos[i]["parent"]][model3d_infos[i]["name"]]["color"];
                        const hexNumber = parseInt(color.substring(1), 16);
                        real_mesh.material.color.setHex(hexNumber);
                        real_mesh.material.color_hex = hexNumber;
                    } else {
                        const no_color = "0xffffff";
                        const hexNumber = parseInt(color.substring(1), 16);
                        real_mesh.material.color.setHex(hexNumber);
                        real_mesh.material.color_hex = hexNumber;
                    }
                    
                    
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

    function changeTexture(object, url, normal_url, height_url,color, opacity,roughness,metalness,translationX,translationY,rotation,scaleX,scaleY,normalScale) {

        console.log("Color: " + color);
        console.log("Opacity: " + opacity);
        console.log("Roughness: " + roughness);
        console.log("Metalness: " + metalness);
        console.log("Translation X: " + translationX);
        console.log("Translation Y: " + translationY);
        console.log("Rotation: " + rotation);
        console.log("Scale X: " + scaleX);
        console.log("Scale Y: " + scaleY);
        console.log("Normal Scale: " + normalScale);
        
        const hexNumber = parseInt(color.substring(1), 16);
        object.traverse((node) => {
            console.log(node);
            if (node.isMesh) {
                
                const material = new THREE.MeshStandardMaterial();

                if (Array.isArray(material)) {
                    material.forEach((mat) => {
                        const texturemap = new THREE.TextureLoader().load(url);
                        texturemap.wrapS = THREE.RepeatWrapping; 
                        texturemap.wrapT = THREE.RepeatWrapping; 

                        // WIP
                        const normalmap = new THREE.TextureLoader().load(normal_url);
                        const heightmap = new THREE.TextureLoader().load(height_url);
                        normalmap.wrapS = THREE.RepeatWrapping; 
                        normalmap.wrapT = THREE.RepeatWrapping; 
                        heightmap.wrapS = THREE.RepeatWrapping;
                        heightmap.wrapT = THREE.RepeatWrapping;
                        // normalmap.repeat.set(length, width); heightmap.repeat.set(length, width);
                        mat.map = texturemap;
                        mat.normalMap = normalmap;
                        mat.normalScale = new THREE.Vector2(0.1, 0.1);
                        
                        mat.displacementMap = heightmap;
                        mat.displacementScale = 0.00;
                        // WIP

                        mat.transparent= true;
                        mat.needsUpdate = true;
                        mat.color.setHex(hexNumber);
                        mat.emissive.setHex(0x000000);
                        mat.emissive.setRGB(0,0,0);
                        mat.transparent=true;
                        mat.opacity=opacity;
                        mat.roughness=roughness;
                        mat.metalness=metalness;
                        mat.map.offset.x=translationX;
                        mat.map.offset.y=translationY;
                        mat.normalMap.offset.x=translationX;
                        mat.normalMap.offset.y=translationY;
                        mat.displacementMap.offset.x=translationX;
                        mat.displacementMap.offset.y=translationY;

                        mat.map.rotation=rotation;
                        mat.normalMap.rotation=rotation;
                        mat.displacementMap.rotation=rotation;

                        mat.map.scaleX=scaleX;
                        mat.map.scaleY=scaleY;
                        mat.normalMap.scaleX=scaleX;
                        mat.normalMap.scaleY=scaleY;
                        mat.displacementMap.scaleX=scaleX;
                        mat.displacementMap.scaleY = scaleY;

                        mat.normalScale = new THREE.Vector2(normalScale, normalScale);




                        mat.emissiveIntensity=0;
                    });
                } else {
                    // BUG ( TypeError: Cannot read properties of null (reading 'toArray')) is somewhere here
                    const texturemap = new THREE.TextureLoader().load(url);
                    const normalmap = new THREE.TextureLoader().load(normal_url);
                    const heightmap = new THREE.TextureLoader().load(height_url);

                    texturemap.wrapS = THREE.RepeatWrapping; normalmap.wrapS = THREE.RepeatWrapping; heightmap.wrapS = THREE.RepeatWrapping;
                    texturemap.wrapT = THREE.RepeatWrapping; normalmap.wrapT = THREE.RepeatWrapping; heightmap.wrapT = THREE.RepeatWrapping;

                    material.map = texturemap;
                    material.normalMap = normalmap;
                    material.displacementMap = heightmap;

                    material.needsUpdate = true;
                    material.transparent= true;

                    material.color.setHex(hexNumber);
                    material.emissive.setHex(0x000000);
                    // material.color=null; //The bug is here in this lil crap
                    material.emissive.setRGB(0,0,0);
                    material.emissiveIntensity=0;

                    material.opacity=opacity;
                    material.roughness=roughness;
                    material.metalness=metalness;
                    material.map.offset.x=translationX;
                    material.map.offset.y=translationY;
                    material.normalMap.offset.x=translationX;
                    material.normalMap.offset.y=translationY;
                    material.displacementMap.offset.x=translationX;
                    material.displacementMap.offset.y=translationY;

                    material.map.rotation=rotation;
                    material.normalMap.rotation=rotation;
                    material.displacementMap.rotation=rotation;

                    material.map.scaleX=scaleX;
                    material.map.scaleY=scaleY;
                    material.normalMap.scaleX=scaleX;
                    material.normalMap.scaleY=scaleY;
                    material.displacementMap.scaleX=scaleX;
                    material.displacementMap.scaleY = scaleY;

                    material.displacementScale = 0.00;

                    material.normalScale = new THREE.Vector2(normalScale, normalScale);
                }
                node.material=material;
                node=node;
            }
        });
        object=object;
        console.log(object);
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

        controls.minDistance = 0.1;
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
            //information_panel.displayTexturePart();

        } else {
            selectedPart.model.children[0].material = originalSelectedMaterial;
            highlightedPart = null;
            selectedPart = null; 
        }

        
    }




</script>



-->
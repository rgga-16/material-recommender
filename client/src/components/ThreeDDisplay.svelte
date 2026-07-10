<script>

    import * as THREE from 'three';
    import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
    import { TransformControls } from 'three/addons/controls/TransformControls.js';
    import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
    import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';


    import {get} from 'svelte/store';

    import {curr_rendering_path} from '../stores.js';
	import {curr_texture_parts} from '../stores.js';
	import {curr_textureparts_path} from '../stores.js';
    import {action_history} from '../stores.js';
    import {in_japanese} from '../stores.js';
    import {addToHistory} from '../lib/history.js';
    import {getImage, degreeToRadians} from '../lib/utils.js';
    import {showToast} from '../lib/toast.js';

    import {isDraggingImage} from '../stores.js';
    import {generated_texture_name} from '../stores.js';
    import {object_transforms} from '../stores.js';

    // import {selected_part_name} from '../stores.js'; 
    // import {selected_obj_name} from '../stores.js';
    import {selected_objs_and_parts} from '../stores.js';
    import {objects_3d} from '../stores.js';

    import {transferred_texture_url} from '../stores.js';
    import {transferred_textureimg_url} from '../stores.js';
    import {transferred_texture_name} from '../stores.js';
    

    import {displayWidth} from '../stores.js';
    import {displayHeight} from '../stores.js';

    import { onMount, onDestroy } from 'svelte';
    import { viewport, inspector } from '../lib/registry.js';

    export let current_texture_parts;

    let japanese;
    in_japanese.subscribe(value => {
        japanese = value;
    });

    let width;
    let height;

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
                    showToast("Error in dragging and dropping texture. Please try again.", 'error');
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

            if(japanese) {
                showToast("選択されたオブジェクトがありません。先にオブジェクトを選択してください。", 'error')
            } else {
                showToast("No selected object. Please select an object first.", 'error');
            }
            
        }
    }

    // Declared before the display-size subscriptions below, whose callbacks
    // run synchronously on subscribe and reference renderer/camera.
    let camera, scene, renderer, controls, raycaster;
    let transformControls = null;

    // The App shell feeds these stores from a ResizeObserver on the viewport
    // cell; the canvas always fills that cell exactly.
    displayWidth.subscribe(value => {
        width = value;
        resizeRenderer();
    });

    displayHeight.subscribe(value => {
        height = value;
        resizeRenderer();
    });

    function resizeRenderer() {
        if (!renderer || !camera || !width || !height) return;
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        renderer.setSize(width, height);
    }

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


    let moveMode = false;
    const pointer = new THREE.Vector2();

    /** Toggle scene-composition mode: click an object to attach move/rotate/
     *  scale gizmos ('g'/'r'/'s' keys switch the gizmo while active). */
    export function setMoveMode(on) {
        moveMode = !!on;
        if (!moveMode && transformControls) {
            transformControls.detach();
        }
        return moveMode;
    }

    function saveObjectTransform() {
        const obj = transformControls && transformControls.object;
        if (!obj) return;
        const transforms = { ...(get(object_transforms) || {}) };
        transforms[obj.name] = {
            position: obj.position.toArray(),
            rotation: [obj.rotation.x, obj.rotation.y, obj.rotation.z],
            scale: obj.scale.toArray(),
        };
        object_transforms.set(transforms);
        fetch("/update_transforms", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({"transforms": transforms}),
        }).catch((error) => console.error("Failed to persist transforms", error));
    }

    /** Render one high-resolution frame offscreen and return it as a PNG
     *  dataURL. Replaces the removed Blender rendering path. */
    export function captureScreenshot(scale=2) {
        const gizmoWasVisible = transformControls ? transformControls.visible : false;
        if (transformControls) transformControls.visible = false;
        renderer.setSize(width * scale, height * scale, false);
        renderer.render(scene, camera);
        const dataURL = renderer.domElement.toDataURL("image/png");
        renderer.setSize(width, height, false);
        if (transformControls) transformControls.visible = gizmoWasVisible;
        renderer.render(scene, camera);
        return dataURL;
    }

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
                    "node": current_texture_parts[obj][part]["node"] || null,
                    "is_selectable": current_texture_parts[obj][part]["is_selectable"]
                })
                model3d_infos=model3d_infos
            }
        }
        objects_3d.set(model3d_infos);
    }

    let HIGHLIGHTED;
    let SELECTED_INFOS = [];
    $: SELECTEDS = SELECTED_INFOS.map(item => item.mesh);

    let mouseDown=false;
    let shiftPressed=false;
    let ctrlPressed = false;
    let altPressed = false;

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
            if (model3d_infos[i].mesh) {
                model3d_infos[i].mesh.material.emissive.setHex(0x000000);
            }
        }
    }

    function removeHighlightsFromUnselecteds() {
        for (let i = 0; i < model3d_infos.length; i++) {
            if(!SELECTED_INFOS.includes(model3d_infos[i]) && model3d_infos[i].mesh) {
                model3d_infos[i].mesh.material.emissive.setHex(0x000000);
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
        if (moveMode) {
            const pointed = getPointedObject();
            if (pointed) {
                let root = pointed;
                while (root.parent && !root.is_object_group) {
                    root = root.parent;
                }
                if (root.is_object_group && transformControls) {
                    transformControls.attach(root);
                }
            } else if (transformControls) {
                transformControls.detach();
            }
            return;
        }
        raycaster.setFromCamera(pointer, camera);
        let objects = model3d_infos.filter(item => item && item.model).map(item => item.model);
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
                            if (index === -1) {
                                SELECTEDS.pop();
                            } else {
                                SELECTED_INFOS.push(model3d_infos[index]);
                            }
                            // console.log("Has not been selected yet. Appending it to selected objects.")
                            SELECTEDS=SELECTEDS;
                            SELECTED_INFOS=SELECTED_INFOS;
                            selected_objs_and_parts.set(SELECTED_INFOS);
                            // //information_panel.clearTexturePart();
                        } else if(altPressed) {
                            //If alt is held, this will select all of the objects that are the same as the clicked object.
                            //for example, clicking on a "backrest" will select all other objects that have "backrest" in the name.
                            SELECTEDS.push(clicked_object);
                            const index = model3d_infos.findIndex(item => item.name === clicked_object.model_name && item.parent === clicked_object.model_parent);
                            if (index === -1) {
                                SELECTEDS.pop();
                            } else {
                                SELECTED_INFOS.push(model3d_infos[index]);
                            }

                            let clicked_object_name = clicked_object.model_name;
                            clicked_object_name = clicked_object_name.replace(/\d+/g, '');
                            console.log(clicked_object_name);

                            let clicked_object_parent = clicked_object.model_parent;
                            clicked_object_parent = clicked_object_parent.replace(/\d+/g, '');
                            console.log(clicked_object_parent);

                            for (let i = 0; i < model3d_infos.length; i++) {
                                let object_name = model3d_infos[i].name;
                                object_name = object_name.replace(/\d+/g, '');
                                let parent_name = model3d_infos[i].parent;
                                parent_name = parent_name.replace(/\d+/g, '');

                                if (object_name === clicked_object_name && parent_name === clicked_object_parent) {
                                    if (model3d_infos[i].mesh && !SELECTEDS.includes(model3d_infos[i].mesh)) {
                                        SELECTEDS.push(model3d_infos[i].mesh);
                                        SELECTED_INFOS.push(model3d_infos[i]);
                                        SELECTEDS=SELECTEDS;    
                                        SELECTED_INFOS=SELECTED_INFOS;
                                    }
                                }
                            }
                            selected_objs_and_parts.set(SELECTED_INFOS);
                        
                        } else if (ctrlPressed) {
                            // If ctrl is pressed, we select the entire all components of the object.
                            // For example, if I hold ctrl and click on a bedframe, we also select the other components of the bed.
                            SELECTEDS.push(clicked_object);
                            const index = model3d_infos.findIndex(item => item.name === clicked_object.model_name && item.parent === clicked_object.model_parent);
                            if (index === -1) {
                                SELECTEDS.pop();
                            } else {
                                SELECTED_INFOS.push(model3d_infos[index]);
                            }

                            let clicked_object_parent = clicked_object.model_parent;
                            console.log(clicked_object_parent);

                            for (let i = 0; i < model3d_infos.length; i++) {
                                let parent_name = model3d_infos[i].parent;

                                if (parent_name === clicked_object_parent) {
                                    if (model3d_infos[i].mesh && !SELECTEDS.includes(model3d_infos[i].mesh)) {
                                        SELECTEDS.push(model3d_infos[i].mesh);
                                        SELECTED_INFOS.push(model3d_infos[i]);
                                        SELECTEDS=SELECTEDS;    
                                        SELECTED_INFOS=SELECTED_INFOS;
                                    }
                                }
                            }
                            selected_objs_and_parts.set(SELECTED_INFOS);



                        } else { //If shift is not held, want to select only one object
                            SELECTEDS = [];
                            SELECTED_INFOS = [];
                            SELECTEDS[0] = clicked_object;
                            // console.log(clicked_object);
                            // console.log(model3d_infos);
                            const index = model3d_infos.findIndex(item => item.name === clicked_object.model_name && item.parent === clicked_object.model_parent);
                            // console.log(get(curr_texture_parts));
                            if (index === -1) {
                                SELECTEDS = [];
                                SELECTED_INFOS = [];
                            } else {
                                SELECTED_INFOS[0] = model3d_infos[index];
                            }
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

                    if(altPressed) {
                    //If alt is held, this will select all of the objects that are the same as the clicked object.
                    //for example, clicking on a "backrest" will select all other objects that have "backrest" in the name.
                        let clicked_object_name = clicked_object.model_name;
                        clicked_object_name = clicked_object_name.replace(/\d+/g, '');
                        console.log(clicked_object_name);
                        
                        let clicked_object_parent = clicked_object.model_parent;
                        clicked_object_parent = clicked_object_parent.replace(/\d+/g, '');
                        console.log(clicked_object_parent);

                        console.log("seat cushion".includes(clicked_object_name));

                        for (let i = 0; i < model3d_infos.length; i++) {
                            let object_name = model3d_infos[i].name;
                            object_name = object_name.replace(/\d+/g, '');
                            let parent_name = model3d_infos[i].parent;
                            parent_name = parent_name.replace(/\d+/g, '');

                            if (object_name.includes(clicked_object_name) && parent_name.includes(clicked_object_parent)) {
                                if (model3d_infos[i].mesh && !SELECTEDS.includes(model3d_infos[i].mesh)) {
                                    SELECTEDS.push(model3d_infos[i].mesh);
                                    SELECTED_INFOS.push(model3d_infos[i]);
                                    SELECTEDS=SELECTEDS;    
                                    SELECTED_INFOS=SELECTED_INFOS;
                                }
                            }
                        }
                        selected_objs_and_parts.set(SELECTED_INFOS);

                    } else if (ctrlPressed) {
                        let clicked_object_parent = clicked_object.model_parent;
                        console.log(clicked_object_parent);

                        for (let i = 0; i < model3d_infos.length; i++) {
                            let parent_name = model3d_infos[i].parent;
                            if (parent_name === clicked_object_parent) {
                                if (model3d_infos[i].mesh && !SELECTEDS.includes(model3d_infos[i].mesh)) {
                                    SELECTEDS.push(model3d_infos[i].mesh);
                                    SELECTED_INFOS.push(model3d_infos[i]);
                                    SELECTEDS=SELECTEDS;    
                                    SELECTED_INFOS=SELECTED_INFOS;
                                }
                            }
                        }
                        selected_objs_and_parts.set(SELECTED_INFOS);
                    } else {
                        SELECTEDS[0].material.emissive.setHex(0x000000);
                        SELECTEDS.splice(index, 1);
                        SELECTED_INFOS.splice(index, 1);
                        // console.log("Has been selected. Deselected.")
                        SELECTEDS=SELECTEDS;    
                        SELECTED_INFOS=SELECTED_INFOS;
                        selected_objs_and_parts.set(SELECTED_INFOS);
                        // information_panel.clearTexturePart();
                        removeHighlightsFromUnselecteds();
                    }   
                }
                SELECTEDS=SELECTEDS;    
                SELECTED_INFOS=SELECTED_INFOS;
                selected_objs_and_parts.set(SELECTED_INFOS);
                // //information_panel.clearTexturePart();
            }
        } else {// If the user clicks on an empty space, then we want to deselect the selected object.
            if (SELECTEDS.length > 0) {
                inspector.get()?.clearTexturePart();
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
        // Only raycast against models that have finished loading (item.model is set once the GLTF load callback runs).
        let objects = model3d_infos.filter(item => item && item.model).map(item => item.model);

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
            showToast("Error: Could not find the object in the model3d_infos array.", 'error');
            return;
        }
        let model = model3d_infos[index].mesh;
        if(!model) {
            console.error("Error: model for " + part_name + " has not finished loading.");
            return;
        }

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

        model3d_infos[index].mesh = model;
        objects_3d.set(model3d_infos);

        cloned_texture_parts[object_name][part_name]["mat_name"] = mat_name;
        cloned_texture_parts[object_name][part_name]["mat_image_texture"] = dest_url;
        cloned_texture_parts[object_name][part_name]["mat_normal_texture"] = normalmap_texture_url;
        cloned_texture_parts[object_name][part_name]["mat_height_texture"] = heightmap_texture_url;

        curr_texture_parts.set(cloned_texture_parts);
    }

    async function onPointerMove(event) {
        if (!isMouseOver3DScene(event)) {
            return;
        }

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

    
    // Per-object containers so a whole object (all its parts) can be moved,
    // rotated, or scaled as one unit for scene composition.
    let object_groups = {};

    function getObjectGroup(objName) {
        if (!object_groups[objName]) {
            const group = new THREE.Group();
            group.name = objName;
            group.is_object_group = true;
            const transforms = get(object_transforms) || {};
            const t = transforms[objName];
            if (t) {
                if (t.position) group.position.fromArray(t.position);
                if (t.rotation) group.rotation.set(t.rotation[0], t.rotation[1], t.rotation[2]);
                if (t.scale) group.scale.fromArray(t.scale);
            }
            scene.add(group);
            object_groups[objName] = group;
        }
        return object_groups[objName];
    }

    function applyManifestColor(mesh, info) {
        const entry = (current_texture_parts[info.parent] || {})[info.name];
        let hexNumber = 0xffffff;
        if (entry && entry.color) {
            hexNumber = parseInt(entry.color.substring(1), 16);
        }
        if (mesh.material && mesh.material.color) {
            mesh.material.color.setHex(hexNumber);
            mesh.material.color_hex = hexNumber;
        }
    }

    function registerMesh(info, mesh, rootModel) {
        rootModel.traverse(function(child) {
            child.model_name = info.name;
            child.model_parent = info.parent;
        });
        info.mesh = mesh;
        info.model = rootModel;
    }

    function add_glb_objects() {
        // v2 scenes share one .glb per object: load each unique URL once.
        const shared_gltf_cache = {};

        for (let i = 0; i < model3d_infos.length; i++) {
            const info = model3d_infos[i];
            const glbUrl = info.glb_url;
            const group = getObjectGroup(info.parent);

            if (info.node) {
                // v2 entry: this part is a named mesh inside a shared .glb
                if (!shared_gltf_cache[glbUrl]) {
                    shared_gltf_cache[glbUrl] = new Promise((resolve, reject) => {
                        gltfLoader.load(glbUrl, resolve, undefined, reject);
                    }).then((gltf) => {
                        group.add(gltf.scene);
                        return gltf;
                    });
                }
                shared_gltf_cache[glbUrl].then((gltf) => {
                    let mesh = null;
                    gltf.scene.traverse((child) => {
                        if (!mesh && child.isMesh && child.name === info.node) {
                            mesh = child;
                        }
                    });
                    if (!mesh) {
                        console.error("Mesh node '" + info.node + "' not found in " + glbUrl);
                        return;
                    }
                    // Clone the material so highlighting/texturing one part
                    // never leaks onto parts sharing a glTF material.
                    if (mesh.material) {
                        mesh.material = mesh.material.clone();
                    }
                    registerMesh(info, mesh, mesh);
                    applyManifestColor(mesh, info);
                    model3d_infos = model3d_infos;
                }).catch((error) => {
                    console.error("Failed to load " + glbUrl, error);
                });
            } else {
                // Legacy entry: one .gltf file per part
                gltfLoader.load(glbUrl, (gltf) => {
                    let model = gltf.scene;

                    //Workaround. If the model.children[0] is Object3D, the Mesh is found in model.children[0].children[0].
                    if(model.children[0] instanceof THREE.Object3D && !(model.children[0] instanceof THREE.Mesh)) {
                        model.children[0] = model.children[0].children[0];
                    }
                    const mesh = model.children[0];

                    registerMesh(info, mesh, model);
                    applyManifestColor(mesh, info);
                    group.add(model);
                    model3d_infos = model3d_infos;
                }, undefined, (error) => {
                    console.error("Failed to load " + glbUrl, error);
                });
            }
        }
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
                    // BUG ( TypeError: Cannot read properties of null (reading 'toArray')) was here:
                    // material.color was being set to null further down, which crashes three.js internals
                    // (e.g. Color.toArray()) the next time the material is rendered/updated. material.color
                    // must always remain a valid THREE.Color instance, so we only ever call setHex/setRGB on it.
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
                    material.emissive.setRGB(0,0,0);
                    material.emissiveIntensity=0;

                    material.opacity=opacity;
                    material.roughness=roughness;
                    material.metalness=metalness;
                    if (material.map) {
                        material.map.offset.x=translationX;
                        material.map.offset.y=translationY;
                        material.map.rotation=rotation;
                        material.map.scaleX=scaleX;
                        material.map.scaleY=scaleY;
                    }
                    if (material.normalMap) {
                        material.normalMap.offset.x=translationX;
                        material.normalMap.offset.y=translationY;
                        material.normalMap.rotation=rotation;
                        material.normalMap.scaleX=scaleX;
                        material.normalMap.scaleY=scaleY;
                    }
                    if (material.displacementMap) {
                        material.displacementMap.offset.x=translationX;
                        material.displacementMap.offset.y=translationY;
                        material.displacementMap.rotation=rotation;
                        material.displacementMap.scaleX=scaleX;
                        material.displacementMap.scaleY = scaleY;
                    }

                    material.displacementScale = 0.00;

                    material.normalScale = new THREE.Vector2(normalScale, normalScale);
                }
                node.material=material;
                node=node;
            }
        });
        object=object;
        // console.log(object);
        return object;
    }

    function setup_scene() {
        if (transformControls) {
            transformControls.detach();
        }
        while (scene.children.length > 0) {
            scene.remove(scene.children[0]);
        }
        object_groups = {};
        add_glb_objects();
        const light = new THREE.AmbientLight(0x969696, 0.1);
        scene.add(light);
        if (transformControls) {
            scene.add(transformControls);
        }
    }

    function init() {
        const container = document.getElementById("viewer-3d");
        container.innerHTML = "";
        renderer = new THREE.WebGLRenderer({ alpha: true });
        // renderer.setSize( window.innerWidth/2, window.innerHeight/2); 
        renderer.setSize( width, height); 
        
        container.appendChild( renderer.domElement );

        scene = new THREE.Scene();
        scene.background = new THREE.Color(0x000000); // Set the background to black

        camera = new THREE.PerspectiveCamera( 70, width/height, 0.1, 1000 );
        camera.position.z = 5;

        camera.updateProjectionMatrix();
        
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
            if (event.key === "Shift" && shiftPressed) { // 16 is the key code for the shift key
                shiftPressed = false;
            }
        });
        window.addEventListener('keydown', function(event) {
            if (event.ctrlKey) { // 16 is the key code for the shift key
                ctrlPressed=true;
            }
        });
        window.addEventListener('keyup', function(event) {
            if(!event.ctrlKey && ctrlPressed) {
                ctrlPressed=false;
            }
        });
        window.addEventListener('keydown', function(event) {
            if(event.altKey) {
                altPressed=true;
            }
        });
        window.addEventListener('keyup', function(event) {
            if(!event.altKey && altPressed) {
                altPressed=false;
            }
        });

        renderer.domElement.addEventListener('click', onPointerClick);

        setup_scene();

        const environment = new RoomEnvironment();
        const pmremGenerator = new THREE.PMREMGenerator( renderer );

        scene.background = new THREE.Color( 0x14171c ); // matches the dark viewport well
        scene.environment = pmremGenerator.fromScene( environment ).texture;

        controls = new OrbitControls( camera, renderer.domElement );
        controls.enableZoom=true;
        controls.minDistance=0.0000000001;
        controls.maxDistance=10000;

        let zoomSpeed=1.5;
        let panSpeed=1.5;
        controls.zoomSpeed= zoomSpeed;
        controls.panSpeed= panSpeed;
        // controls.minDistance = 0.1;
        // controls.maxDistance = 10;
        

        controls.mouseButtons = {
            LEFT: null,
            MIDDLE: THREE.MOUSE.PAN,
            RIGHT: THREE.MOUSE.ROTATE
        }

        controls.addEventListener('change', function() {
            controls.zoomSpeed=zoomSpeed;
            controls.panSpeed=panSpeed;
        })

        
        controls.target.set( 0, 0.35, 0 );
        controls.update();

        transformControls = new TransformControls(camera, renderer.domElement);
        transformControls.addEventListener('dragging-changed', function(event) {
            controls.enabled = !event.value;
        });
        transformControls.addEventListener('mouseUp', saveObjectTransform);
        scene.add(transformControls);

        window.addEventListener('keydown', function(event) {
            if (!moveMode || !transformControls || !transformControls.object) return;
            if (event.key === 'g') transformControls.setMode('translate');
            if (event.key === 'r') transformControls.setMode('rotate');
            if (event.key === 's') transformControls.setMode('scale');
        });
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

    onDestroy(
        viewport.register({
            update_3d_scene,
            fullTextureTransferAlgorithm,
            setMoveMode,
            captureScreenshot,
            removeHighlights,
            transferTexture,
        })
    );

</script>

<div id="viewer-3d"></div>


<style>

    #viewer-3d {
        width: inherit;
        height: inherit;
    }

</style>
<script>
	// 3D viewport (runes mode). Rendering/scene plumbing lives in
	// lib/three/{sceneSetup,sceneContent,materials,selection,loaders}.js;
	// this component wires it to the stores, pointer/keyboard input, and the
	// registry surface other modules call into.
	import * as THREE from 'three';
	import { get } from 'svelte/store';
	import { onMount, onDestroy } from 'svelte';

	import {
		curr_texture_parts,
		curr_textureparts_path,
		in_japanese,
		isDraggingImage,
		objects_3d,
		object_transforms,
		selected_objs_and_parts,
		transferred_texture_name,
		transferred_texture_url,
		transferred_textureimg_url,
		displayWidth,
		displayHeight,
	} from '../stores.js';

	import { addToHistory } from '../lib/history.js';
	import { getImage, degreeToRadians } from '../lib/utils.js';
	import { postJson } from '../lib/api.js';
	import { showToast } from '../lib/toast.js';
	import { viewport, inspector } from '../lib/registry.js';

	import { createViewer } from '../lib/three/sceneSetup.js';
	import { createSelection } from '../lib/three/selection.js';
	import { buildPartMaterial, disposeMaterial, DEFAULT_NORMAL_SCALE, DEFAULT_DISPLACEMENT_SCALE } from '../lib/three/materials.js';
	import { loadSceneModels, disposeSceneContent } from '../lib/three/sceneContent.js';

	let { current_texture_parts = {} } = $props();

	let japanese = $derived($in_japanese);
	let dragging = $derived($isDraggingImage);
	let dragged_texture_url = $derived($transferred_texture_url);
	let dragged_textureimg_url = $derived($transferred_textureimg_url);
	let dragged_texture_name = $derived($transferred_texture_name);

	// {name, parent, glb_url, node, is_selectable, mesh?, model?} per part
	let model3d_infos = [];
	let manifest = current_texture_parts;

	let container = null;
	let viewer = null;
	let ambientLight = null;
	let object_groups = {};
	let moveMode = false;
	let HIGHLIGHTED = null;
	let animationFrame = 0;

	const pointer = new THREE.Vector2();
	let mouseDown = false;
	let shiftPressed = false;
	let ctrlPressed = false;
	let altPressed = false;

	const selection = createSelection({
		getInfos: () => model3d_infos,
		onChange: (infos) => selected_objs_and_parts.set(infos),
	});

	// The App shell feeds these stores from a ResizeObserver on the viewport
	// cell; the canvas always fills that cell exactly.
	$effect(() => {
		const w = $displayWidth;
		const h = $displayHeight;
		if (viewer) viewer.resize(w, h);
	});

	// ------------------------------------------------------------ scene setup

	function get_models() {
		model3d_infos = [];
		for (const obj in manifest) {
			for (const part in manifest[obj]) {
				model3d_infos.push({
					name: part,
					parent: obj,
					glb_url: manifest[obj][part]['model'],
					node: manifest[obj][part]['node'] || null,
					is_selectable: manifest[obj][part]['is_selectable'],
				});
			}
		}
		objects_3d.set(model3d_infos);
	}

	// Per-object containers so a whole object (all its parts) can be moved,
	// rotated, or scaled as one unit for scene composition.
	function getObjectGroup(objName) {
		if (!object_groups[objName]) {
			const group = new THREE.Group();
			group.name = objName;
			group.is_object_group = true;
			const t = (get(object_transforms) || {})[objName];
			if (t) {
				if (t.position) group.position.fromArray(t.position);
				if (t.rotation) group.rotation.set(t.rotation[0], t.rotation[1], t.rotation[2]);
				if (t.scale) group.scale.fromArray(t.scale);
			}
			viewer.scene.add(group);
			object_groups[objName] = group;
		}
		return object_groups[objName];
	}

	function setup_scene() {
		viewer.transformControls.detach();
		disposeSceneContent(viewer.scene, new Set([viewer.transformGizmo, ambientLight]));
		object_groups = {};
		loadSceneModels(model3d_infos, {
			renderer: viewer.renderer,
			getGroup: getObjectGroup,
			getEntry: (info) => (manifest[info.parent] || {})[info.name],
			onLoaded: () => objects_3d.set(model3d_infos),
		});
	}

	export function update_3d_scene() {
		selection.clear();
		manifest = get(curr_texture_parts);
		get_models();
		setup_scene();
	}

	// ------------------------------------------------------- texture transfer

	/** Apply a texture set to one part and persist it into the current scene
	 *  dir. Returns the persisted {img_url, normal_url, height_url}. */
	export async function transferTexture(object_name, part_name, mat_name, image_path, normal_path, height_path) {
		const cloned_texture_parts = get(curr_texture_parts);
		const info = model3d_infos.find(
			(item) => item.name === part_name && item.parent === object_name
		);
		if (!info) {
			console.error(`transferTexture: unknown part ${object_name}/${part_name}`);
			showToast(`Error: could not find ${object_name}/${part_name} in the scene.`, 'error');
			return null;
		}
		if (!info.mesh) {
			console.error(`transferTexture: model for ${part_name} has not finished loading.`);
			return null;
		}

		const entry = cloned_texture_parts[object_name][part_name];
		const material = buildPartMaterial({
			imageUrl: await getImage(image_path),
			normalUrl: normal_path ? await getImage(normal_path) : null,
			heightUrl: height_path ? await getImage(height_path) : null,
			color: entry['color'] || '#FFFFFF',
			opacity: entry['opacity'] ?? 1,
			roughness: entry['roughness'] ?? 0.5,
			metalness: entry['metalness'] ?? 0.0,
			normalScale: entry['normalScale'] ?? DEFAULT_NORMAL_SCALE,
			displacementScale: entry['displacementScale'] ?? DEFAULT_DISPLACEMENT_SCALE,
			offsetX: entry['offsetX'] ?? 0,
			offsetY: entry['offsetY'] ?? 0,
			rotation: degreeToRadians(entry['rotation'] ?? 0),
			repeatX: entry['scaleX'] ?? 1,
			repeatY: entry['scaleY'] ?? 1,
		});
		info.mesh.traverse((node) => {
			if (node.isMesh) {
				disposeMaterial(node.material);
				node.material = material;
			}
		});

		// Persist the applied set into the current scene dir so the scene
		// stays self-contained on disk.
		const moved = await postJson('/transfer_texture', {
			src_url: image_path,
			curr_textureparts_path: get(curr_textureparts_path),
		});

		entry['mat_name'] = mat_name;
		entry['mat_image_texture'] = moved.img_url;
		entry['mat_normal_texture'] = moved.normal_url;
		entry['mat_height_texture'] = moved.height_url;
		curr_texture_parts.set(cloned_texture_parts);
		objects_3d.set(model3d_infos);
		return moved;
	}

	function clearDragState() {
		transferred_texture_name.set(null);
		transferred_texture_url.set(null);
		transferred_textureimg_url.set(null);
		isDraggingImage.set(false);
	}

	/** Apply the currently dragged texture to every selected part, recording
	 *  one history entry per part. */
	export async function fullTextureTransferAlgorithm() {
		if (selection.infos.length === 0) {
			clearDragState();
			showToast(japanese
				? '選択されたオブジェクトがありません。先にオブジェクトを選択してください。'
				: 'No selected object. Please select an object first.', 'error');
			return;
		}
		if (!dragged_texture_name || !dragged_textureimg_url) {
			clearDragState();
			showToast('Error in dragging and dropping texture. Please try again.', 'error');
			return;
		}

		const texture_name = dragged_texture_name;
		const textureimg_url = dragged_textureimg_url;
		const dot = textureimg_url.lastIndexOf('.');
		const base = textureimg_url.slice(0, dot);
		const ext = textureimg_url.slice(dot + 1);
		const texturenormal_url = `${base}_normal.${ext}`;
		const textureheight_url = `${base}_height.${ext}`;

		for (const info of [...selection.infos]) {
			const entry = get(curr_texture_parts)[info.parent][info.name];
			const old_values = [
				entry['mat_name'] ?? null,
				entry['mat_image_texture'] ?? null,
				entry['mat_normal_texture'] ?? null,
				entry['mat_height_texture'] ?? null,
			];

			const moved = await transferTexture(
				info.parent, info.name, texture_name,
				textureimg_url, texturenormal_url, textureheight_url
			);
			if (!moved) continue;

			await addToHistory('Change Texture',
				info.parent, info.name,
				['mat_name', 'mat_image_texture', 'mat_normal_texture', 'mat_height_texture'],
				old_values,
				[texture_name, moved.img_url, moved.normal_url, moved.height_url]);
		}
		clearDragState();
	}

	// --------------------------------------------------- selection/highlight

	export function removeHighlights() {
		if (HIGHLIGHTED) {
			HIGHLIGHTED.material.emissive.setHex(0x000000);
			HIGHLIGHTED = null;
		}
		for (const info of model3d_infos) {
			if (info.mesh) {
				info.mesh.material.emissive.setHex(0x000000);
				info.mesh.material.emissiveIntensity = 0;
			}
		}
		selection.clear();
	}

	function removeHighlightsFromUnselecteds() {
		for (const info of model3d_infos) {
			if (info.mesh && !selection.infos.includes(info)) {
				info.mesh.material.emissive.setHex(0x000000);
				info.mesh.material.emissiveIntensity = 0;
			}
		}
	}

	function getPointedObject() {
		viewer.raycaster.setFromCamera(pointer, viewer.camera);
		// Only raycast against models that have finished loading.
		const objects = model3d_infos.filter((item) => item && item.model).map((item) => item.model);
		let intersects;
		try {
			intersects = viewer.raycaster.intersectObjects(objects, true);
		} catch (error) {
			// A model can be mid-load (children without layers yet).
			console.warn('raycast skipped:', error);
			intersects = [];
		}
		return intersects.length > 0 ? intersects[0].object : null;
	}

	function isObjectSelectable(object) {
		const info = model3d_infos.find(
			(item) => item.name === object.model_name && item.parent === object.model_parent
		);
		return !!(info && info.is_selectable);
	}

	function clearSelectionAndHighlights() {
		for (const mesh of selection.meshes()) {
			mesh.material.emissive.setHex(0x000000);
		}
		selection.clear();
		removeHighlightsFromUnselecteds();
	}

	function onPointerClick(event) {
		event.preventDefault();
		if (!isMouseOver3DScene(event)) return;

		if (moveMode) {
			const pointed = getPointedObject();
			if (pointed) {
				let root = pointed;
				while (root.parent && !root.is_object_group) {
					root = root.parent;
				}
				if (root.is_object_group) viewer.transformControls.attach(root);
			} else {
				viewer.transformControls.detach();
			}
			return;
		}

		const clicked = getPointedObject();
		if (!clicked) {
			// Empty space: deselect everything.
			if (selection.infos.length > 0) {
				inspector.get()?.clearTexturePart();
				clearSelectionAndHighlights();
			}
			return;
		}

		if (!isObjectSelectable(clicked)) {
			if (selection.infos.length > 0) clearSelectionAndHighlights();
			return;
		}

		selection.click(clicked, { shift: shiftPressed, ctrl: ctrlPressed, alt: altPressed });
		removeHighlightsFromUnselecteds();
	}

	function highlightObject() {
		for (const mesh of selection.meshes()) {
			mesh.material.emissive.setRGB(0, 0, 1);
			mesh.material.emissiveIntensity = 0.2;
		}

		const object = getPointedObject();
		if (object) {
			if (HIGHLIGHTED !== object) {
				if (HIGHLIGHTED) {
					HIGHLIGHTED.material.emissive.setRGB(0, 0, 0);
					HIGHLIGHTED.material.emissiveIntensity = 0;
				}
				if (isObjectSelectable(object)) {
					HIGHLIGHTED = object;
					HIGHLIGHTED.material.emissive.setRGB(1, 0, 0);
					HIGHLIGHTED.material.emissiveIntensity = 0.2;
				} else {
					HIGHLIGHTED = null;
				}
			}
		} else if (HIGHLIGHTED) {
			HIGHLIGHTED.material.emissive.setRGB(0, 0, 0);
			HIGHLIGHTED.material.emissiveIntensity = 0;
			HIGHLIGHTED = null;
		}
	}

	// -------------------------------------------------------- move mode etc.

	/** Toggle scene-composition mode: click an object to attach move/rotate/
	 *  scale gizmos ('g'/'r'/'s' keys switch the gizmo while active). */
	export function setMoveMode(on) {
		moveMode = !!on;
		if (!moveMode && viewer) viewer.transformControls.detach();
		return moveMode;
	}

	function saveObjectTransform() {
		const obj = viewer.transformControls.object;
		if (!obj) return;
		const transforms = { ...(get(object_transforms) || {}) };
		transforms[obj.name] = {
			position: obj.position.toArray(),
			rotation: [obj.rotation.x, obj.rotation.y, obj.rotation.z],
			scale: obj.scale.toArray(),
		};
		object_transforms.set(transforms);
		postJson('/update_transforms', { transforms })
			.catch((error) => console.error('Failed to persist transforms', error));
	}

	export function captureScreenshot(scale = 2) {
		return viewer.captureScreenshot(get(displayWidth), get(displayHeight), scale);
	}

	// ----------------------------------------------------------------- input

	function isMouseOver3DScene(event) {
		const rect = viewer.renderer.domElement.getBoundingClientRect();
		return (event.clientX >= rect.left && event.clientX <= rect.right &&
			event.clientY >= rect.top && event.clientY <= rect.bottom);
	}

	function onPointerMove(event) {
		if (!isMouseOver3DScene(event)) return;
		const rect = viewer.renderer.domElement.getBoundingClientRect();
		pointer.x = ((event.clientX - rect.left) / get(displayWidth)) * 2 - 1;
		pointer.y = -((event.clientY - rect.top) / get(displayHeight)) * 2 + 1;

		if (mouseDown && dragging && dragged_texture_url && dragged_textureimg_url && dragged_texture_name) {
			fullTextureTransferAlgorithm();
		}
	}

	function onMouseDown(event) {
		if (event.button === 0) mouseDown = true;
	}

	function onMouseUp(event) {
		if (event.button === 0) mouseDown = false;
	}

	function onKeyDown(event) {
		if (event.key === 'Shift') shiftPressed = true;
		if (event.ctrlKey) ctrlPressed = true;
		if (event.altKey) altPressed = true;

		if (moveMode && viewer.transformControls.object) {
			if (event.key === 'g') viewer.transformControls.setMode('translate');
			if (event.key === 'r') viewer.transformControls.setMode('rotate');
			if (event.key === 's') viewer.transformControls.setMode('scale');
		}
	}

	function onKeyUp(event) {
		if (event.key === 'Shift') shiftPressed = false;
		if (!event.ctrlKey) ctrlPressed = false;
		if (!event.altKey) altPressed = false;
	}

	// ------------------------------------------------------------- lifecycle

	onMount(() => {
		get_models();

		viewer = createViewer(container, get(displayWidth) || 1, get(displayHeight) || 1);
		ambientLight = new THREE.AmbientLight(0x969696, 0.1);
		viewer.scene.add(ambientLight);

		viewer.transformControls.addEventListener('dragging-changed', (event) => {
			viewer.controls.enabled = !event.value;
		});
		viewer.transformControls.addEventListener('mouseUp', saveObjectTransform);

		setup_scene();

		window.addEventListener('mousedown', onMouseDown);
		window.addEventListener('mouseup', onMouseUp);
		window.addEventListener('mousemove', onPointerMove);
		window.addEventListener('keydown', onKeyDown);
		window.addEventListener('keyup', onKeyUp);
		viewer.renderer.domElement.addEventListener('click', onPointerClick);

		function render() {
			animationFrame = requestAnimationFrame(render);
			viewer.controls.update();
			viewer.camera.updateMatrixWorld();
			highlightObject();
			viewer.renderer.render(viewer.scene, viewer.camera);
		}
		render();

		return () => {
			cancelAnimationFrame(animationFrame);
			window.removeEventListener('mousedown', onMouseDown);
			window.removeEventListener('mouseup', onMouseUp);
			window.removeEventListener('mousemove', onPointerMove);
			window.removeEventListener('keydown', onKeyDown);
			window.removeEventListener('keyup', onKeyUp);
			viewer.renderer.domElement.removeEventListener('click', onPointerClick);
			disposeSceneContent(viewer.scene, new Set([viewer.transformGizmo]));
			viewer.dispose();
			viewer = null;
		};
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

<div id="viewer-3d" bind:this={container}></div>

<style>
	#viewer-3d {
		width: inherit;
		height: inherit;
	}
</style>

// Loading scene models (GLB/GLTF/OBJ/FBX/STL) into per-object groups, and
// disposing scene content on rebuild so GPU resources are actually released.
import * as THREE from 'three';
import { loadGltf, loadModel } from './loaders.js';
import { disposeMaterial } from './materials.js';

/** Remove and deep-dispose every scene child not in `keep`. */
export function disposeSceneContent(scene, keep) {
	for (const child of [...scene.children]) {
		if (keep.has(child)) continue;
		child.traverse((node) => {
			if (node.isMesh) {
				if (node.geometry) node.geometry.dispose();
				disposeMaterial(node.material);
			}
		});
		scene.remove(child);
	}
}

export function applyManifestColor(mesh, entry) {
	let hexNumber = 0xffffff;
	if (entry && entry.color) {
		hexNumber = parseInt(entry.color.substring(1), 16);
	}
	if (mesh.material && mesh.material.color) {
		mesh.material.color.setHex(hexNumber);
		mesh.material.color_hex = hexNumber;
	}
}

export function registerMesh(info, mesh, rootModel) {
	rootModel.traverse((child) => {
		child.model_name = info.name;
		child.model_parent = info.parent;
	});
	info.mesh = mesh;
	info.model = rootModel;
}

/**
 * Load every part in `infos` into the scene.
 *
 * v2 entries (info.node set) share one .glb per object — each unique URL is
 * fetched once and parts pick their named mesh out of it. Legacy entries are
 * one .gltf file per part. Materials are cloned per part so highlighting or
 * texturing one part never leaks onto parts sharing a glTF material.
 *
 * getEntry(info) returns the part's manifest entry (for its color);
 * getGroup(parent) returns the THREE.Group that owns that object;
 * onLoaded(info) fires after each part is registered.
 */
export function loadSceneModels(infos, { renderer, getGroup, getEntry, onLoaded }) {
	const sharedGltfCache = {};

	for (const info of infos) {
		const group = getGroup(info.parent);

		if (info.node) {
			if (!sharedGltfCache[info.glb_url]) {
				// loadModel dispatches on extension (.glb/.gltf/.obj/.fbx/.stl)
				// and normalizes mesh names/UVs the same way the upload parser
				// did, so manifest "node" keys resolve for every format.
				sharedGltfCache[info.glb_url] = loadModel(info.glb_url, renderer).then((root) => {
					group.add(root);
					return root;
				});
			}
			sharedGltfCache[info.glb_url].then((root) => {
				let mesh = null;
				root.traverse((child) => {
					if (!mesh && child.isMesh && child.name === info.node) {
						mesh = child;
					}
				});
				if (!mesh) {
					console.error(`Mesh node '${info.node}' not found in ${info.glb_url}`);
					return;
				}
				if (mesh.material) {
					mesh.material = mesh.material.clone();
				}
				registerMesh(info, mesh, mesh);
				applyManifestColor(mesh, getEntry(info));
				onLoaded(info);
			}).catch((error) => {
				console.error(`Failed to load ${info.glb_url}`, error);
			});
		} else {
			loadGltf(info.glb_url, renderer).then((gltf) => {
				const model = gltf.scene;
				// Legacy export quirk: the mesh may sit one level deeper.
				if (model.children[0] instanceof THREE.Object3D &&
						!(model.children[0] instanceof THREE.Mesh)) {
					model.children[0] = model.children[0].children[0];
				}
				const mesh = model.children[0];
				registerMesh(info, mesh, model);
				applyManifestColor(mesh, getEntry(info));
				group.add(model);
				onLoaded(info);
			}).catch((error) => {
				console.error(`Failed to load ${info.glb_url}`, error);
			});
		}
	}
}

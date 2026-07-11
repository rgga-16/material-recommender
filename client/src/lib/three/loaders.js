// Shared asset loaders for the 3D viewport. One GLTFLoader (with DRACO /
// meshopt / KTX2 decoding) and one TextureLoader for the whole app — the old
// code built a fresh TextureLoader per texture change.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { KTX2Loader } from 'three/addons/loaders/KTX2Loader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';

let gltfLoader = null;
const textureLoader = new THREE.TextureLoader();

/** Lazily build the shared GLTFLoader. Decoder files are served from
 * static/draco and static/basis (copied into public/ at build time), so
 * compressed GLBs work fully offline. */
export function getGltfLoader(renderer) {
	if (!gltfLoader) {
		gltfLoader = new GLTFLoader();
		gltfLoader.setDRACOLoader(new DRACOLoader().setDecoderPath('/draco/'));
		gltfLoader.setMeshoptDecoder(MeshoptDecoder);
		if (renderer) {
			gltfLoader.setKTX2Loader(
				new KTX2Loader().setTranscoderPath('/basis/').detectSupport(renderer)
			);
		}
	}
	return gltfLoader;
}

export function loadGltf(url, renderer) {
	return getGltfLoader(renderer).loadAsync(url);
}

function loadWrapped(url) {
	const texture = textureLoader.load(url);
	texture.wrapS = THREE.RepeatWrapping;
	texture.wrapT = THREE.RepeatWrapping;
	return texture;
}

/** Diffuse/albedo maps carry color and must be tagged sRGB, or they render
 * washed out under color management. */
export function loadColorTexture(url) {
	const texture = loadWrapped(url);
	texture.colorSpace = THREE.SRGBColorSpace;
	return texture;
}

/** Normal/height/roughness maps are data, not color — leave them linear. */
export function loadDataTexture(url) {
	return loadWrapped(url);
}

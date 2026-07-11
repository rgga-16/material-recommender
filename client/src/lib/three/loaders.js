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

// ---------------------------------------------------------------------------
// Multi-format model loading (.glb/.gltf/.obj/.fbx/.stl)
// ---------------------------------------------------------------------------

export const MODEL_EXTENSIONS = ['glb', 'gltf', 'obj', 'fbx', 'stl'];

function modelExt(name) {
	return (name.split('?')[0].split('.').pop() || '').toLowerCase();
}

function baseName(name) {
	const file = name.split('?')[0].split('/').pop() || 'model';
	return file.replace(/\.[^.]+$/, '');
}

/** Box-project UVs onto a geometry that has none (common for STL and some
 * OBJ exports) so generated textures still map onto it. Each vertex is
 * projected along its dominant normal axis, normalized to the bounding box. */
export function boxProjectUVs(geometry) {
	geometry.computeBoundingBox();
	if (!geometry.attributes.normal) geometry.computeVertexNormals();
	const bbox = geometry.boundingBox;
	const size = new THREE.Vector3();
	bbox.getSize(size);
	size.x = size.x || 1;
	size.y = size.y || 1;
	size.z = size.z || 1;

	const position = geometry.attributes.position;
	const normal = geometry.attributes.normal;
	const uv = new Float32Array(position.count * 2);
	for (let i = 0; i < position.count; i++) {
		const nx = Math.abs(normal.getX(i));
		const ny = Math.abs(normal.getY(i));
		const nz = Math.abs(normal.getZ(i));
		const x = position.getX(i);
		const y = position.getY(i);
		const z = position.getZ(i);
		let u, v;
		if (nx >= ny && nx >= nz) {
			u = (z - bbox.min.z) / size.z;
			v = (y - bbox.min.y) / size.y;
		} else if (ny >= nx && ny >= nz) {
			u = (x - bbox.min.x) / size.x;
			v = (z - bbox.min.z) / size.z;
		} else {
			u = (x - bbox.min.x) / size.x;
			v = (y - bbox.min.y) / size.y;
		}
		uv[i * 2] = u;
		uv[i * 2 + 1] = v;
	}
	geometry.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
}

/** Make any loaded model behave like our GLTF scenes: every mesh has a
 * deterministic non-empty name (manifest "node" keys must match between
 * upload-time parsing and scene loading), UVs exist, and multi-material
 * arrays are flattened (selection highlighting writes material.emissive). */
export function normalizeModel(root, fallbackBase) {
	let counter = 0;
	root.traverse((child) => {
		if (!child.isMesh) return;
		counter += 1;
		if (!child.name) child.name = `${fallbackBase || 'part'}_${counter}`;
		if (Array.isArray(child.material)) child.material = child.material[0];
		if (child.geometry && !child.geometry.attributes.uv) {
			boxProjectUVs(child.geometry);
		}
	});
	return root;
}

/** Load a model of any supported format from a URL; resolves to a normalized
 * Object3D root (loader modules for non-glTF formats load on demand). */
export async function loadModel(url, renderer) {
	const ext = modelExt(url);
	let root;
	if (ext === 'glb' || ext === 'gltf') {
		root = (await loadGltf(url, renderer)).scene;
	} else if (ext === 'obj') {
		const { OBJLoader } = await import('three/addons/loaders/OBJLoader.js');
		root = await new OBJLoader().loadAsync(url);
	} else if (ext === 'fbx') {
		const { FBXLoader } = await import('three/addons/loaders/FBXLoader.js');
		root = await new FBXLoader().loadAsync(url);
	} else if (ext === 'stl') {
		const { STLLoader } = await import('three/addons/loaders/STLLoader.js');
		const geometry = await new STLLoader().loadAsync(url);
		const mesh = new THREE.Mesh(geometry, new THREE.MeshStandardMaterial());
		mesh.name = baseName(url);
		root = new THREE.Group();
		root.add(mesh);
	} else {
		throw new Error(`Unsupported model format: .${ext}`);
	}
	return normalizeModel(root, baseName(url));
}

/** Parse an in-memory File of any supported format (upload preview); resolves
 * to the same normalized root that loadModel() will produce for its URL. */
export async function parseModelFile(file) {
	const ext = modelExt(file.name);
	let root;
	if (ext === 'glb' || ext === 'gltf') {
		const buffer = await file.arrayBuffer();
		root = await new Promise((resolve, reject) => {
			getGltfLoader().parse(buffer, '', (gltf) => resolve(gltf.scene), reject);
		});
	} else if (ext === 'obj') {
		const { OBJLoader } = await import('three/addons/loaders/OBJLoader.js');
		root = new OBJLoader().parse(await file.text());
	} else if (ext === 'fbx') {
		const { FBXLoader } = await import('three/addons/loaders/FBXLoader.js');
		root = new FBXLoader().parse(await file.arrayBuffer(), '');
	} else if (ext === 'stl') {
		const { STLLoader } = await import('three/addons/loaders/STLLoader.js');
		const geometry = new STLLoader().parse(await file.arrayBuffer());
		const mesh = new THREE.Mesh(geometry, new THREE.MeshStandardMaterial());
		mesh.name = baseName(file.name);
		root = new THREE.Group();
		root.add(mesh);
	} else {
		throw new Error(`Unsupported model format: .${ext}`);
	}
	return normalizeModel(root, baseName(file.name));
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

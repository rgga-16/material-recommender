// PBR material construction and disposal for scene parts.
import * as THREE from 'three';
import { loadColorTexture, loadDataTexture } from './loaders.js';

// Normal maps default to full strength so generated maps are actually
// visible; displacement gets a subtle default (it only shows on meshes with
// enough vertices, and larger values crack low-poly geometry).
export const DEFAULT_NORMAL_SCALE = 1.0;
export const DEFAULT_DISPLACEMENT_SCALE = 0.02;

const MAP_KEYS = ['map', 'normalMap', 'displacementMap', 'roughnessMap',
	'metalnessMap', 'aoMap'];

/** Dispose a material and every texture it owns. */
export function disposeMaterial(material) {
	if (!material) return;
	for (const mat of Array.isArray(material) ? material : [material]) {
		for (const key of MAP_KEYS) {
			if (mat[key]) mat[key].dispose();
		}
		mat.dispose();
	}
}

/** Apply the manifest's UV transform to every map on the material. */
export function applyMapTransforms(material, { offsetX = 0, offsetY = 0,
	rotation = 0, repeatX = 1, repeatY = 1 } = {}) {
	for (const key of ['map', 'normalMap', 'displacementMap', 'aoMap']) {
		const map = material[key];
		if (!map) continue;
		map.offset.set(offsetX, offsetY);
		map.rotation = rotation;
		map.repeat.set(repeatX, repeatY);
	}
}

/**
 * Build the MeshStandardMaterial for a part from its manifest entry and
 * texture URLs. Missing normal/height URLs are simply skipped.
 */
export function buildPartMaterial({ imageUrl, normalUrl, heightUrl, aoUrl,
	color = '#FFFFFF', opacity = 1, roughness = 0.5, metalness = 0,
	normalScale = DEFAULT_NORMAL_SCALE,
	displacementScale = DEFAULT_DISPLACEMENT_SCALE,
	offsetX = 0, offsetY = 0, rotation = 0, repeatX = 1, repeatY = 1 }) {
	const material = new THREE.MeshStandardMaterial();

	if (imageUrl) material.map = loadColorTexture(imageUrl);
	if (normalUrl) {
		material.normalMap = loadDataTexture(normalUrl);
		material.normalScale = new THREE.Vector2(normalScale, normalScale);
	}
	if (heightUrl) {
		material.displacementMap = loadDataTexture(heightUrl);
		material.displacementScale = displacementScale;
	}
	if (aoUrl) {
		material.aoMap = loadDataTexture(aoUrl);
		// Sample AO with the base UV set — these models have no second set.
		material.aoMap.channel = 0;
		material.aoMapIntensity = 1.0;
	}

	// material.color must always remain a valid THREE.Color instance —
	// three.js crashes internally if it's ever set to null.
	material.color.setHex(parseInt(color.substring(1), 16));
	material.transparent = true;
	material.opacity = opacity;
	material.roughness = roughness;
	material.metalness = metalness;
	material.emissive.setRGB(0, 0, 0);
	material.emissiveIntensity = 0;

	applyMapTransforms(material, { offsetX, offsetY, rotation, repeatX, repeatY });
	material.needsUpdate = true;
	return material;
}

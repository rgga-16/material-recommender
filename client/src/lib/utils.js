export function dictToString(input_dict) {
	let temp = "";
	for (const key in input_dict) {
		temp += input_dict[key];
	}
	return temp;
}

export function isDict(obj) {
	return typeof obj === 'object' && obj !== null && !Array.isArray(obj);
}

export function degreeToRadians(degrees) {
	return degrees * (Math.PI/180);
}

import { imageUrl } from './api.js';

/** Browser-loadable URL for a server image path. Generated files are
 * overwritten in place by the server, so always cache-bust. Kept async for
 * compatibility with existing callers (it used to fetch a blob). */
export async function getImage(path) {
	if (!path) return null;
	return imageUrl(path, { bust: true });
}

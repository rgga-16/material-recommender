// Undo/redo system. Each history action stores {name, object, part,
// properties: {prop: {old, new}}}. Undo applies the "old" side of the action
// at currentIndex and steps back; redo steps forward and applies the "new"
// side. Property behavior is table-driven (PROPERTY_ACTIONS) instead of the
// former ~450 lines of duplicated per-property if/else chains.
import { action_history, selected_objs_and_parts } from '../stores.js';
import { curr_texture_parts, objects_3d } from '../stores.js';
import { viewport } from './registry.js';
import { get } from 'svelte/store';
import { degreeToRadians } from './utils.js';

let all_3d_objects;
objects_3d.subscribe(value => {
	all_3d_objects = value;
});

let history;
action_history.subscribe(value => {
	history = value;
});

/** Apply fn to the texture maps that carry UV transforms (guarded — parts
 *  without normal/height maps only get the base map updated). */
function forTransformMaps(material, fn) {
	fn(material.map);
	if (material.normalMap) fn(material.normalMap);
	if (material.displacementMap) fn(material.displacementMap);
}

// How each history property is written back onto the live three.js material.
// Keys are the lowercase suffix of the action name ("Change <key>").
const PROPERTY_ACTIONS = {
	opacity: {
		prop: 'opacity',
		apply: (material, v) => {
			material.transparent = true;
			material.opacity = v;
		},
	},
	roughness: {
		prop: 'roughness',
		apply: (material, v) => (material.roughness = v),
	},
	metalness: {
		prop: 'metalness',
		apply: (material, v) => (material.metalness = v),
	},
	color: {
		prop: 'color',
		apply: (material, v) => {
			const hexNumber = parseInt(v.substring(1), 16);
			material.color.setHex(hexNumber);
			material.color_hex = hexNumber;
		},
	},
	normalscale: {
		prop: 'normalScale',
		apply: (material, v) => material.normalScale.set(v, v),
	},
	displacementscale: {
		prop: 'displacementScale',
		apply: (material, v) => (material.displacementScale = v),
	},
	offsetx: {
		prop: 'offsetX',
		apply: (material, v) => forTransformMaps(material, (map) => (map.offset.x = v)),
	},
	offsety: {
		prop: 'offsetY',
		apply: (material, v) => forTransformMaps(material, (map) => (map.offset.y = v)),
	},
	rotation: {
		prop: 'rotation',
		apply: (material, v) => forTransformMaps(material, (map) => (map.rotation = degreeToRadians(v))),
	},
	scalex: {
		prop: 'scaleX',
		apply: (material, v) => forTransformMaps(material, (map) => (map.repeat.x = v)),
	},
	scaley: {
		prop: 'scaleY',
		apply: (material, v) => forTransformMaps(material, (map) => (map.repeat.y = v)),
	},
};

/** "Change Texture" actions restore full texture-map sets through the server's
 *  action-history storage, then re-run the viewport texture transfer. */
async function applyTextureAction(action, index, old_or_new) {
	const props = action.properties;
	const response = await fetch('/retrieve_textures_from_action_history', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({
			current_history_index: index,
			old_or_new: old_or_new,
			old_img_path: props['mat_image_texture'][old_or_new],
			old_normal_path: props['mat_normal_texture'][old_or_new],
			old_height_path: props['mat_height_texture'][old_or_new],
		}),
	});
	const json = await response.json();
	viewport.get()?.transferTexture(
		action.object,
		action.part,
		props['mat_name'][old_or_new],
		json['updated_old_img_path'],
		json['updated_old_normal_path'],
		json['updated_old_height_path']
	);
}

async function applyAction(action, index, old_or_new) {
	const name = action.name.toLowerCase();

	if (name === 'change texture') {
		await applyTextureAction(action, index, old_or_new);
		return;
	}

	const entry = PROPERTY_ACTIONS[name.replace(/^change /, '')];
	if (!entry) {
		// Actions without a live-material effect (e.g. "Change mat_finish")
		// only move the history index — same as the old fall-through behavior.
		return;
	}

	const value = action.properties[entry.prop][old_or_new];
	const idx = all_3d_objects.findIndex(
		(item) => item.name === action.part && item.parent === action.object
	);
	if (idx === -1) return;

	// Write the restored value back into the scene manifest…
	curr_texture_parts.update((parts) => {
		parts[action.object][action.part][entry.prop] = value;
		return parts;
	});
	// …and onto the live three.js material. info.mesh is the part's mesh in
	// both scene formats (legacy one-file-per-part and v2 shared-GLB).
	objects_3d.update((objects) => {
		if (objects[idx].mesh) entry.apply(objects[idx].mesh.material, value);
		return objects;
	});
	// Select the affected part so the change is visible in the inspector.
	selected_objs_and_parts.set([all_3d_objects[idx]]);
}

export async function undoAction() {
	if (history.currentIndex <= -1) return;

	const index = history.currentIndex;
	await applyAction(history.actions[index], index, 'old');

	action_history.update((h) => ({ ...h, currentIndex: h.currentIndex - 1 }));
}

export async function redoAction() {
	if (history.currentIndex >= history.actions.length - 1) return;

	// Step forward first (matches the original ordering: the server's texture
	// retrieval is keyed on the post-increment index).
	action_history.update((h) => ({ ...h, currentIndex: h.currentIndex + 1 }));

	const index = history.currentIndex;
	await applyAction(history.actions[index], index, 'new');
}

export async function addToHistory(action_name, object, part, properties, old_values, new_values) {
	if (properties.length != old_values.length || properties.length != new_values.length) {
		throw new Error('addToHistory: properties, old_values, and new_values must be the same length');
	}
	let properties_dict = {};
	for (let i = 0; i < properties.length; i++) {
		properties_dict[properties[i]] = {
			old: old_values[i],
			new: new_values[i],
		};
	}
	let action = {
		name: action_name,
		object: object,
		part: part,
		properties: properties_dict,
	};

	if (action.name.toLowerCase() == 'change texture') {
		// Texture files get copied into server-side history storage so undo can
		// restore them even after the working files are overwritten.
		const response = await fetch('/add_old_and_new_textures_to_action_history', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				current_history_index: history.currentIndex,
				old_img_path: action.properties['mat_image_texture']['old'],
				old_normal_path: action.properties['mat_normal_texture']['old'],
				old_height_path: action.properties['mat_height_texture']['old'],
				new_img_path: action.properties['mat_image_texture']['new'],
				new_normal_path: action.properties['mat_normal_texture']['new'],
				new_height_path: action.properties['mat_height_texture']['new'],
			}),
		});
		const json = await response.json();
		action.properties['mat_image_texture']['old'] = json['updated_old_img_path'];
		action.properties['mat_normal_texture']['old'] = json['updated_old_normal_path'];
		action.properties['mat_height_texture']['old'] = json['updated_old_height_path'];

		action.properties['mat_image_texture']['new'] = json['updated_new_img_path'];
		action.properties['mat_normal_texture']['new'] = json['updated_new_normal_path'];
		action.properties['mat_height_texture']['new'] = json['updated_new_height_path'];
	}

	action_history.update((h) => {
		const newActions = h.actions;
		newActions.push(action);
		return {
			actions: newActions,
			currentIndex: newActions.length - 1,
		};
	});
}

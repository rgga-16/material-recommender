import App from './App.svelte';

import {action_history, selected_objs_and_parts, information_panel_global} from './stores.js';
import {curr_texture_parts, objects_3d} from './stores.js';
import { threed_display_global } from './stores.js';
import {get} from 'svelte/store';


// const DEEPL_AUTHKEY='2c0ea470-3cef-d714-4176-cde832a9b2f5:fx';
// const translator = new deepl.Translator(DEEPL_AUTHKEY);
let information_panel;
information_panel_global.subscribe(value => {
	information_panel = value;
});

let all_3d_objects;
objects_3d.subscribe(value => {
	all_3d_objects = value;
});

let current_texture_parts;
curr_texture_parts.subscribe(value => {
	current_texture_parts = value;
});

let history; 
action_history.subscribe(value => {
	history = value;
});

let three_display;
threed_display_global.subscribe(value => {
	three_display = value;
});

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

export async function undoAction() {

	if (history.currentIndex > -1) {
		
		// Undo action here
		const action = history.actions[history.currentIndex];
		const object = action.object;
		const part = action.part;
		const properties_dict = action.properties;
		const currentIndex = history.currentIndex;
		const old_or_new = "old";

		if(action.name.toLowerCase() == "change texture"){
			const response = await fetch("/retrieve_textures_from_action_history", {
				method: "POST",
				headers: {"Content-Type": "application/json"},
				body: JSON.stringify({
					"current_history_index": history.currentIndex,
					"old_or_new":old_or_new,
					"old_img_path": history.actions[history.currentIndex]["properties"]["mat_image_texture"][old_or_new],
					"old_normal_path": history.actions[history.currentIndex]["properties"]["mat_normal_texture"][old_or_new],
					"old_height_path": history.actions[history.currentIndex]["properties"]["mat_height_texture"][old_or_new],
				}),
			});
			const json = await response.json();
			const updated_old_img_path= await json["updated_old_img_path"];
			const updated_old_normal_path = await json["updated_old_normal_path"];
			const updated_old_height_path = await json["updated_old_height_path"];
			const updated_old_mat_name = history.actions[history.currentIndex]["properties"]["mat_name"][old_or_new];

			three_display.transferTexture(object, part, updated_old_mat_name,updated_old_img_path, updated_old_normal_path, updated_old_height_path);
			
		} else if (action.name.toLowerCase()=="change opacity") {
			// Get the 3D model by accessing 3D objects store using object and part variables.
			const idx = all_3d_objects.findIndex(item => item.name === part && item.parent === object);
			let object_3d = all_3d_objects[idx]; //Get the 3D model
			const old_opacity = properties_dict["opacity"][old_or_new]; // Set the old opacity of the 3D model
			//Update the opacity of the 3D model in the curr_texture_parts store
			curr_texture_parts.update(value => {
				value[object][part]["opacity"] = old_opacity;
				return value;
			});
			//Update the opacity of the 3D model in the objects_3d store
			objects_3d.update(objects => {
				objects[idx].model.children[0].material.transparent= true;
				objects[idx].model.children[0].material.opacity = old_opacity;
				return objects;
			})
			// Make the 3D model the selected object, so that we can see the change in the Information Panel
			selected_objs_and_parts.set([object_3d]);
			information_panel.displayTexturePart();
			console.log("undoed opacity!");
		} else if (action.name.toLowerCase()=="change roughness") {
			// Get the 3D model by accessing 3D objects store using object and part variables.
			const idx = all_3d_objects.findIndex(item => item.name === part && item.parent === object);
			let object_3d = all_3d_objects[idx]; //Get the 3D model
			const old_roughness = properties_dict["roughness"][old_or_new]; // Set the old roughness of the 3D model
			//Update the roughness of the 3D model in the curr_texture_parts store
			curr_texture_parts.update(value => {
				value[object][part]["roughness"] = old_roughness;
				return value;
			});
			//Update the roughness of the 3D model in the objects_3d store
			objects_3d.update(objects => {
				objects[idx].model.children[0].material.roughness = old_roughness;
				return objects;
			})
			// Make the 3D model the selected object, so that we can see the change in the Information Panel
			selected_objs_and_parts.set([object_3d]);
			information_panel.displayTexturePart();
			console.log("undoed roughness!");
		} else if (action.name.toLowerCase()=="change metalness") {
			// Get the 3D model by accessing 3D objects store using object and part variables.
			const idx = all_3d_objects.findIndex(item => item.name === part && item.parent === object);
			let object_3d = all_3d_objects[idx]; //Get the 3D model
			const old_metalness = properties_dict["metalness"][old_or_new]; // Set the old metalness of the 3D model	
			//Update the metalness of the 3D model in the curr_texture_parts store
			curr_texture_parts.update(value => {
				value[object][part]["metalness"] = old_metalness;
				return value;
			});
			//Update the metalness of the 3D model in the objects_3d store
			objects_3d.update(objects => {
				objects[idx].model.children[0].material.metalness = old_metalness;
				return objects;
			})
			// Make the 3D model the selected object, so that we can see the change in the Information Panel
			selected_objs_and_parts.set([object_3d]);
			information_panel.displayTexturePart();
			console.log("undoed metalness!");
		} else if (action.name.toLowerCase()=="change color") {
			// Get the 3D model by accessing 3D objects store using object and part variables.
			const idx = all_3d_objects.findIndex(item => item.name === part && item.parent === object);
			let object_3d = all_3d_objects[idx]; //Get the 3D model

			const old_color = properties_dict["color"][old_or_new]; // Set the old color of the 3D model
			//Update the color of the 3D model in the curr_texture_parts store
			curr_texture_parts.update(value => {
				value[object][part]["color"] = old_color;
				return value;
			});
			//Update the color of the 3D model in the objects_3d store
			objects_3d.update(objects => {
				objects[idx].model.children[0].material.color.setHex(old_color);
				return objects;
			})
			// Make the 3D model the selected object, so that we can see the change in the Information Panel
			selected_objs_and_parts.set([object_3d]);
			information_panel.displayTexturePart();
			console.log("undoed color!");
		}

		// Update the action history 
		action_history.update(history => {
			return {
				...history,
				currentIndex: history.currentIndex - 1
			};
		});
		console.log(get(action_history));
	}

}

export async function redoAction() {
	if (history.currentIndex < history.actions.length - 1) {
		// Update the action history 
		action_history.update(history => {
			return {
				...history,
				currentIndex: history.currentIndex + 1
			};
		});
		console.log(get(action_history));
		
		// Redo action here
		// const action = history.actions[history.currentIndex + 1];
		const action = history.actions[history.currentIndex];
		const object = action.object;
		const part = action.part;
		const properties_dict = action.properties;
		const currentIndex = history.currentIndex;
		const old_or_new = "new";

		if(action.name.toLowerCase() == "change texture"){
			const response = await fetch("/retrieve_textures_from_action_history", {
				method: "POST",
				headers: {"Content-Type": "application/json"},
				body: JSON.stringify({
					"current_history_index": history.currentIndex,
					"old_or_new":old_or_new,
					"old_img_path": history.actions[history.currentIndex]["properties"]["mat_image_texture"][old_or_new],
					"old_normal_path": history.actions[history.currentIndex]["properties"]["mat_normal_texture"][old_or_new],
					"old_height_path": history.actions[history.currentIndex]["properties"]["mat_height_texture"][old_or_new],
				}),
			});
			const json = await response.json();
			const updated_old_img_path= await json["updated_old_img_path"];
			const updated_old_normal_path = await json["updated_old_normal_path"];
			const updated_old_height_path = await json["updated_old_height_path"];
			const updated_old_mat_name = history.actions[history.currentIndex]["properties"]["mat_name"][old_or_new];
			three_display.transferTexture(object, part, updated_old_mat_name, updated_old_img_path, updated_old_normal_path, updated_old_height_path);
		} else if (action.name.toLowerCase()=="change opacity") {
			// Get the 3D model by accessing 3D objects store using object and part variables.
			const idx = all_3d_objects.findIndex(item => item.name === part && item.parent === object);
			let object_3d = all_3d_objects[idx]; //Get the 3D model
			const old_opacity = properties_dict["opacity"][old_or_new]; // Set the old opacity of the 3D model
			//Update the opacity of the 3D model in the curr_texture_parts store
			curr_texture_parts.update(value => {
				value[object][part]["opacity"] = old_opacity;
				return value;
			});
			//Update the opacity of the 3D model in the objects_3d store
			objects_3d.update(objects => {
				objects[idx].model.children[0].material.transparent= true;
				objects[idx].model.children[0].material.opacity = old_opacity;
				return objects;
			})
			// Make the 3D model the selected object, so that we can see the change in the Information Panel
			selected_objs_and_parts.set([object_3d]);
			information_panel.displayTexturePart();
			console.log("undoed opacity!");
		} else if (action.name.toLowerCase()=="change roughness") {
			// Get the 3D model by accessing 3D objects store using object and part variables.
			const idx = all_3d_objects.findIndex(item => item.name === part && item.parent === object);
			let object_3d = all_3d_objects[idx]; //Get the 3D model
			const old_roughness = properties_dict["roughness"][old_or_new]; // Set the old roughness of the 3D model
			//Update the roughness of the 3D model in the curr_texture_parts store
			curr_texture_parts.update(value => {
				value[object][part]["roughness"] = old_roughness;
				return value;
			});
			//Update the roughness of the 3D model in the objects_3d store
			objects_3d.update(objects => {
				objects[idx].model.children[0].material.roughness = old_roughness;
				return objects;
			})
			// Make the 3D model the selected object, so that we can see the change in the Information Panel
			selected_objs_and_parts.set([object_3d]);
			information_panel.displayTexturePart();
			console.log("undoed roughness!");
		} else if (action.name.toLowerCase()=="change metalness") {
			// Get the 3D model by accessing 3D objects store using object and part variables.
			const idx = all_3d_objects.findIndex(item => item.name === part && item.parent === object);
			let object_3d = all_3d_objects[idx]; //Get the 3D model
			const old_metalness = properties_dict["metalness"][old_or_new]; // Set the old metalness of the 3D model	
			//Update the metalness of the 3D model in the curr_texture_parts store
			curr_texture_parts.update(value => {
				value[object][part]["metalness"] = old_metalness;
				return value;
			});
			//Update the metalness of the 3D model in the objects_3d store
			objects_3d.update(objects => {
				objects[idx].model.children[0].material.metalness = old_metalness;
				return objects;
			})
			// Make the 3D model the selected object, so that we can see the change in the Information Panel
			selected_objs_and_parts.set([object_3d]);
			information_panel.displayTexturePart();
			console.log("undoed metalness!");
		} else if (action.name.toLowerCase()=="change color") {
			// Get the 3D model by accessing 3D objects store using object and part variables.
			const idx = all_3d_objects.findIndex(item => item.name === part && item.parent === object);
			let object_3d = all_3d_objects[idx]; //Get the 3D model

			const old_color = properties_dict["color"][old_or_new]; // Set the old color of the 3D model
			//Update the color of the 3D model in the curr_texture_parts store
			curr_texture_parts.update(value => {
				value[object][part]["color"] = old_color;
				return value;
			});
			//Update the color of the 3D model in the objects_3d store
			objects_3d.update(objects => {
				objects[idx].model.children[0].material.color.setHex(old_color);
				return objects;
			})
			// Make the 3D model the selected object, so that we can see the change in the Information Panel
			selected_objs_and_parts.set([object_3d]);
			information_panel.displayTexturePart();
			console.log("undoed color!");
		}
	}
}

export async function getImage(path) {
	let path_blob = null;
	try {   
		const response = await fetch("/get_image", {
			method: "POST",
			headers: {"Content-Type": "application/json"},
			body: JSON.stringify({
				"image_data": path,
			}),
		});
		const blob = await response.blob();
		path_blob = URL.createObjectURL(blob);
	} catch (error) {
		console.error(error);
	}
	return path_blob
}

export async function addToHistory(action_name,object,part, properties, old_values, new_values){

	if(properties.length != old_values.length || properties.length != new_values.length){
		throw new Error("addToHistory: properties, old_values, and new_values must be the same length") ;
	}

	let properties_dict = {};
	for(let i = 0; i < properties.length; i++){
		properties_dict[properties[i]] = {
			"old": old_values[i],
			"new": new_values[i]
		}
	}

	let action = {
		"name": action_name,
		"object": object,
		"part": part,
		"properties": properties_dict
	}

	// console.log(history.actions[history.currentIndex]["properties"]);

	if (action.name.toLowerCase() == "change texture") {
		const response = await fetch("/add_old_and_new_textures_to_action_history", {
			method: "POST",
			headers: {"Content-Type": "application/json"},
			body: JSON.stringify({
				"current_history_index": history.currentIndex,
				"old_img_path": action["properties"]["mat_image_texture"]["old"],
				"old_normal_path": action["properties"]["mat_normal_texture"]["old"],
				"old_height_path": action["properties"]["mat_height_texture"]["old"],
				"new_img_path": action["properties"]["mat_image_texture"]["new"],
				"new_normal_path": action["properties"]["mat_normal_texture"]["new"],
				"new_height_path": action["properties"]["mat_height_texture"]["new"],
			}),
		});
		const json = await response.json();
		action["properties"]["mat_image_texture"]["old"] = await json["updated_old_img_path"];
		action["properties"]["mat_normal_texture"]["old"] = await json["updated_old_normal_path"];
		action["properties"]["mat_height_texture"]["old"] = await json["updated_old_height_path"];

		action["properties"]["mat_image_texture"]["new"] = await json["updated_new_img_path"];
		action["properties"]["mat_normal_texture"]["new"] = await json["updated_new_normal_path"];
		action["properties"]["mat_height_texture"]["new"] = await json["updated_new_height_path"];
	}


	action_history.update(history => {
		// const newActions = history.actions.slice(0, history.currentIndex+1);
		const newActions = history.actions;
		newActions.push(action);
		return {
			actions: newActions,
			currentIndex: newActions.length-1
		}
	});
	console.log(get(action_history));
}

export async function translate(source_lang, target_lang, text) {
	const response = await fetch("/translate", {
		method: "POST",
		headers: {"Content-Type": "application/json"},
		body: JSON.stringify({
			"text": text,
			"target_lang": target_lang,
			"source_lang": source_lang
		}),
	});
	const json = await response.json();
	const translated_text = await json['text'];
	// console.log(translated_text);
	return translated_text;
}



const app = new App({
	target: document.body,
	props: {
		name: 'world'
	}
});

export default app;
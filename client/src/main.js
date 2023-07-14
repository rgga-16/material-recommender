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

function degreeToRadians(degrees) {
	return degrees * (Math.PI/180);
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

		// Get the 3D model by accessing 3D objects store using object and part variables.
		const idx = all_3d_objects.findIndex(item => item.name === part && item.parent === object);
		let object_3d = all_3d_objects[idx]; //Get the 3D model
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
			console.log("undoed opacity!");
		} else if (action.name.toLowerCase()=="change roughness") {
			
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
			console.log("undoed metalness!");
		} else if (action.name.toLowerCase()=="change color") {

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
			console.log("undoed color!");
		} else if (action.name.toLowerCase()=="change normalscale") {
			const old_normalScale = properties_dict["normalScale"][old_or_new]; // Set the old normalScale of the 3D model
			//Update the normalScale of the 3D model in the curr_texture_parts store
			curr_texture_parts.update(value => {
				value[object][part]["normalScale"] = old_normalScale;
				return value;
			});
			//Update the normalScale of the 3D model in the objects_3d store
			objects_3d.update(objects => {
				objects[idx].model.children[0].material.normalScale.set(old_normalScale, old_normalScale);
				return objects;
			});
			// Make the 3D model the selected object, so that we can see the change in the Information Panel
			selected_objs_and_parts.set([object_3d]);
			console.log("undoed normalScale!");
		} else if (action.name.toLowerCase()=="change displacementscale") {	
			const old_displacementScale = properties_dict["displacementScale"][old_or_new]; // Set the old displacementScale of the 3D model
			//Update the displacementScale of the 3D model in the curr_texture_parts store
			curr_texture_parts.update(value => {
				value[object][part]["displacementScale"] = old_displacementScale;
				return value;
			});
			//Update the displacementScale of the 3D model in the objects_3d store
			objects_3d.update(objects => {
				objects[idx].model.children[0].material.displacementScale = old_displacementScale;
				return objects;
			});
			// Make the 3D model the selected object, so that we can see the change in the Information Panel
			selected_objs_and_parts.set([object_3d]);
			console.log("undoed displacementScale!");
		} else if (action.name.toLowerCase() == "change offsetx") {
			const old_offsetx = properties_dict["offsetX"][old_or_new]; // Set the old offsetx of the 3D model
			//Update the offsetx of the 3D model in the curr_texture_parts store
			curr_texture_parts.update(value => {
				value[object][part]["offsetX"] = old_offsetx;
				return value;
			});
			//Update the offsetx of the 3D model in the objects_3d store
			objects_3d.update(objects => {
				objects[idx].model.children[0].material.map.offset.x = old_offsetx;
				if (objects[idx].model.children[0].material.normalMap) objects[idx].model.children[0].material.normalMap.offset.x = old_offsetx;
				if (objects[idx].model.children[0].material.displacementMap) objects[idx].model.children[0].material.displacementMap.offset.x = old_offsetx;
				return objects;
			});
			selected_objs_and_parts.set([object_3d]);
			console.log("undoed offsetx!");

		} else if (action.name.toLowerCase() == "change offsety") {
			const old_offsety = properties_dict["offsetY"][old_or_new]; // Set the old offsety of the 3D model
			//Update the offsety of the 3D model in the curr_texture_parts store
			curr_texture_parts.update(value => {
				value[object][part]["offsetY"] = old_offsety;
				return value;
			});
			//Update the offsety of the 3D model in the objects_3d store
			objects_3d.update(objects => {
				objects[idx].model.children[0].material.map.offset.y = old_offsety;
				if (objects[idx].model.children[0].material.normalMap) objects[idx].model.children[0].material.normalMap.offset.y = old_offsety;
				if (objects[idx].model.children[0].material.displacementMap) objects[idx].model.children[0].material.displacementMap.offset.y = old_offsety;
				return objects;
			});
			selected_objs_and_parts.set([object_3d]);
			console.log("undoed offsety!");

		} else if (action.name.toLowerCase() =="change rotation") {
			const old_rotation = properties_dict["rotation"][old_or_new]; // Set the old rotation of the 3D model
			//Update the rotation of the 3D model in the curr_texture_parts store
			curr_texture_parts.update(value => {
				value[object][part]["rotation"] = old_rotation;
				return value;
			});
			//Update the rotation of the 3D model in the objects_3d store
			objects_3d.update(objects => {
				objects[idx].model.children[0].material.map.rotation = degreeToRadians(old_rotation);
				if (objects[idx].model.children[0].material.normalMap) objects[idx].model.children[0].material.normalMap.rotation = degreeToRadians(old_rotation);
				if (objects[idx].model.children[0].material.displacementMap) objects[idx].model.children[0].material.displacementMap.rotation = degreeToRadians(old_rotation);
				return objects;
			});
			selected_objs_and_parts.set([object_3d]);
			console.log("undoed rotation!");
		} else if(action.name.toLowerCase() == "change scalex") {
			const old_scalex = properties_dict["scaleX"][old_or_new]; // Set the old scalex of the 3D model
			//Update the scalex of the 3D model in the curr_texture_parts store
			curr_texture_parts.update(value => {
				value[object][part]["scaleX"] = old_scalex;
				return value;
			}	);
			//Update the scalex of the 3D model in the objects_3d store
			objects_3d.update(objects => {
				objects[idx].model.children[0].material.map.repeat["x"] = old_scalex;
				if (objects[idx].model.children[0].material.normalMap) objects[idx].model.children[0].material.normalMap.repeat["x"] = old_scalex;
				if (objects[idx].model.children[0].material.displacementMap) objects[idx].model.children[0].material.displacementMap.repeat["x"] = old_scalex;
				return objects;
			});
			selected_objs_and_parts.set([object_3d]);
			console.log("undoed scalex!");
		} else if(action.name.toLowerCase() == "change scaley") {
			const old_scaley = properties_dict["scaleY"][old_or_new]; // Set the old scalex of the 3D model
			//Update the scalex of the 3D model in the curr_texture_parts store
			curr_texture_parts.update(value => {
				value[object][part]["scaleY"] = old_scaley;
				return value;
			}	);
			//Update the scalex of the 3D model in the objects_3d store
			objects_3d.update(objects => {
				objects[idx].model.children[0].material.map.repeat["y"] = old_scaley;
				if (objects[idx].model.children[0].material.normalMap) objects[idx].model.children[0].material.normalMap.repeat["y"] = old_scaley;
				if (objects[idx].model.children[0].material.displacementMap) objects[idx].model.children[0].material.displacementMap.repeat["y"] = old_scaley;
				return objects;
			});
			selected_objs_and_parts.set([object_3d]);
			console.log("undoed scaley!");
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

		// Get the 3D model by accessing 3D objects store using object and part variables.
		const idx = all_3d_objects.findIndex(item => item.name === part && item.parent === object);
		let object_3d = all_3d_objects[idx]; //Get the 3D model

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
			console.log("redoed opacity!");
		} else if (action.name.toLowerCase()=="change roughness") {
			
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
			console.log("redoed roughness!");
		} else if (action.name.toLowerCase()=="change metalness") {
			
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
			console.log("redoed metalness!");
		} else if (action.name.toLowerCase()=="change color") {

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
			console.log("redoed color!");
		} else if (action.name.toLowerCase()=="change normalscale") {
			const old_normalScale = properties_dict["normalScale"][old_or_new]; // Set the old normalScale of the 3D model
			//Update the normalScale of the 3D model in the curr_texture_parts store
			curr_texture_parts.update(value => {
				value[object][part]["normalScale"] = old_normalScale;
				return value;
			});
			//Update the normalScale of the 3D model in the objects_3d store
			objects_3d.update(objects => {
				objects[idx].model.children[0].material.normalScale.set(old_normalScale, old_normalScale);
				return objects;
			});
			// Make the 3D model the selected object, so that we can see the change in the Information Panel
			selected_objs_and_parts.set([object_3d]);
			console.log("redoed normalScale!");
		} else if (action.name.toLowerCase()=="change displacementscale") {	
			const old_displacementScale = properties_dict["displacementScale"][old_or_new]; // Set the old displacementScale of the 3D model
			//Update the displacementScale of the 3D model in the curr_texture_parts store
			curr_texture_parts.update(value => {
				value[object][part]["displacementScale"] = old_displacementScale;
				return value;
			});
			//Update the displacementScale of the 3D model in the objects_3d store
			objects_3d.update(objects => {
				objects[idx].model.children[0].material.displacementScale = old_displacementScale;
				return objects;
			});
			// Make the 3D model the selected object, so that we can see the change in the Information Panel
			selected_objs_and_parts.set([object_3d]);
			console.log("redoed displacementScale!");
		} else if (action.name.toLowerCase() == "change offsetx") {
			const old_offsetx = properties_dict["offsetX"][old_or_new]; // Set the old offsetx of the 3D model
			//Update the offsetx of the 3D model in the curr_texture_parts store
			curr_texture_parts.update(value => {
				value[object][part]["offsetX"] = old_offsetx;
				return value;
			});
			//Update the offsetx of the 3D model in the objects_3d store
			objects_3d.update(objects => {
				objects[idx].model.children[0].material.map.offset.x = old_offsetx;
				objects[idx].model.children[0].material.normalMap.offset.x = old_offsetx;
				objects[idx].model.children[0].material.displacementMap.offset.x = old_offsetx;
				return objects;
			});
			selected_objs_and_parts.set([object_3d]);
			console.log("undoed offsetx!");

		} else if (action.name.toLowerCase() == "change offsety") {
			const old_offsety = properties_dict["offsetY"][old_or_new]; // Set the old offsety of the 3D model
			//Update the offsety of the 3D model in the curr_texture_parts store
			curr_texture_parts.update(value => {
				value[object][part]["offsetY"] = old_offsety;
				return value;
			});
			//Update the offsety of the 3D model in the objects_3d store
			objects_3d.update(objects => {
				objects[idx].model.children[0].material.map.offset.y = old_offsety;
				objects[idx].model.children[0].material.normalMap.offset.y = old_offsety;
				objects[idx].model.children[0].material.displacementMap.offset.y = old_offsety;
				return objects;
			});
			selected_objs_and_parts.set([object_3d]);
			console.log("undoed offsety!");

		} else if (action.name.toLowerCase() =="change rotation") {
			const old_rotation = properties_dict["rotation"][old_or_new]; // Set the old rotation of the 3D model
			//Update the rotation of the 3D model in the curr_texture_parts store
			curr_texture_parts.update(value => {
				value[object][part]["rotation"] = old_rotation;
				return value;
			});
			//Update the rotation of the 3D model in the objects_3d store
			objects_3d.update(objects => {
				objects[idx].model.children[0].material.map.rotation = degreeToRadians(old_rotation);
				objects[idx].model.children[0].material.normalMap.rotation = degreeToRadians(old_rotation);
				objects[idx].model.children[0].material.displacementMap.rotation = degreeToRadians(old_rotation);
				return objects;
			});
			selected_objs_and_parts.set([object_3d]);
			console.log("undoed rotation!");
		} else if(action.name.toLowerCase() == "change scalex") {
			const old_scalex = properties_dict["scaleX"][old_or_new]; // Set the old scalex of the 3D model
			//Update the scalex of the 3D model in the curr_texture_parts store
			curr_texture_parts.update(value => {
				value[object][part]["scaleX"] = old_scalex;
				return value;
			}	);
			//Update the scalex of the 3D model in the objects_3d store
			objects_3d.update(objects => {
				objects[idx].model.children[0].material.map.repeat.x = old_scalex;
				objects[idx].model.children[0].material.normalMap.repeat.x = old_scalex;
				objects[idx].model.children[0].material.displacementMap.repeat.x = old_scalex;
				return objects;
			});
			selected_objs_and_parts.set([object_3d]);
			console.log("undoed scalex!");
		} else if(action.name.toLowerCase() == "change scaley") {
			const old_scaley = properties_dict["scaleY"][old_or_new]; // Set the old scalex of the 3D model
			//Update the scalex of the 3D model in the curr_texture_parts store
			curr_texture_parts.update(value => {
				value[object][part]["scaleY"] = old_scaley;
				return value;
			}	);
			//Update the scalex of the 3D model in the objects_3d store
			objects_3d.update(objects => {
				objects[idx].model.children[0].material.map.repeat.y = old_scaley;
				objects[idx].model.children[0].material.normalMap.repeat.y = old_scaley;
				objects[idx].model.children[0].material.displacementMap.repeat.y = old_scaley;
				return objects;
			});
			selected_objs_and_parts.set([object_3d]);
			console.log("undoed scaley!");
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
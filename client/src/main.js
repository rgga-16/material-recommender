import App from './App.svelte';

import {action_history} from './stores.js';
import {curr_texture_parts} from './stores.js';
import { threed_display_global } from './stores.js';
import {get} from 'svelte/store';

let history; 
action_history.subscribe(value => {
	history = value;
});

let three_display;
threed_display_global.subscribe(value => {
	three_display = value;
});

export async function undoAction() {

	if (history.currentIndex > -1) {
		
		// Undo action here
		const action = history.actions[history.currentIndex];
		// action = {
		// 	"name": action_name,
		// 	"object": object,
		// 	"part": part,
		// 	"properties": properties_dict
		// }
		const object = action.object;
		const part = action.part;
		const properties_dict = action.properties;
		const currentIndex = history.currentIndex;
		const old_or_new = "old";

		if(action.name == "Change Texture"){
			const response = await fetch("/retrieve_textures_from_action_history", {
				method: "POST",
				headers: {"Content-Type": "application/json"},
				body: JSON.stringify({
					"current_history_index": history.currentIndex,
					"old_or_new":old_or_new,
					"old_img_path": history.actions[history.currentIndex]["properties"]["mat_image_texture"]["old"],
					"old_normal_path": history.actions[history.currentIndex]["properties"]["mat_normal_texture"]["old"],
					"old_height_path": history.actions[history.currentIndex]["properties"]["mat_height_texture"]["old"],
				}),
			});
			const json = await response.json();
			const updated_old_img_path= await json["updated_old_img_path"];
			const updated_old_normal_path = await json["updated_old_normal_path"];
			const updated_old_height_path = await json["updated_old_height_path"];

			three_display.transferTexture(object, part, updated_old_img_path, updated_old_normal_path, updated_old_height_path);
			
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
		// Redo action here
		const action = history.actions[history.currentIndex + 1];

		if(action.name == "Change Texture"){

		}

		// Update the action history 
		action_history.update(history => {
			return {
				...history,
				currentIndex: history.currentIndex + 1
			};
		});
		console.log(get(action_history));
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

	action_history.update(history => {
		const newActions = history.actions.slice(0, history.currentIndex+1);
		newActions.push(action);
		return {
			actions: newActions,
			currentIndex: newActions.length-1
		}
	});

	console.log(history.actions[history.currentIndex]["properties"]);

	if (action.name == "Change Texture") {
		const response = await fetch("/add_old_and_new_textures_to_action_history", {
			method: "POST",
			headers: {"Content-Type": "application/json"},
			body: JSON.stringify({
				"current_history_index": history.currentIndex,
				"old_img_path": history.actions[history.currentIndex]["properties"]["mat_image_texture"]["old"],
				"old_normal_path": history.actions[history.currentIndex]["properties"]["mat_normal_texture"]["old"],
				"old_height_path": history.actions[history.currentIndex]["properties"]["mat_height_texture"]["old"],
				"new_img_path": history.actions[history.currentIndex]["properties"]["mat_image_texture"]["new"],
				"new_normal_path": history.actions[history.currentIndex]["properties"]["mat_normal_texture"]["new"],
				"new_height_path": history.actions[history.currentIndex]["properties"]["mat_height_texture"]["new"],
			}),
		});
		const json = await response.json();
		history.actions[history.currentIndex]["properties"]["mat_image_texture"]["old"] = await json["updated_old_img_path"];
		history.actions[history.currentIndex]["properties"]["mat_normal_texture"]["old"] = await json["updated_old_normal_path"];
		history.actions[history.currentIndex]["properties"]["mat_height_texture"]["old"] = await json["updated_old_height_path"];

		history.actions[history.currentIndex]["properties"]["mat_image_texture"]["new"] = await json["updated_new_img_path"];
		history.actions[history.currentIndex]["properties"]["mat_normal_texture"]["new"] = await json["updated_new_normal_path"];
		history.actions[history.currentIndex]["properties"]["mat_height_texture"]["new"] = await json["updated_new_height_path"];
		action_history.set(history);
	}

	console.log(get(action_history));

}



const app = new App({
	target: document.body,
	props: {
		name: 'world'
	}
});

export default app;
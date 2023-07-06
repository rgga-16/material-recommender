import App from './App.svelte';

import {action_history} from './stores.js';
import {get} from 'svelte/store';


export function addToHistory(action_name,object,part, properties, old_values, new_values){
	let history = get(action_history);

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

	history.push({
		"name": action_name,
		"object": object,
		"part": part,
		"properties": properties_dict
	})
	history=history;

	action_history.set(history);
	console.log(get(action_history));

}



const app = new App({
	target: document.body,
	props: {
		name: 'world'
	}
});

export default app;
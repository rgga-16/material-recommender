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

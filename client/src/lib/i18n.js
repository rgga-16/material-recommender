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

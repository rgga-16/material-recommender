export async function translate(source_lang, target_lang, text) {
	try {
		const response = await fetch("/translate", {
			method: "POST",
			headers: {"Content-Type": "application/json"},
			body: JSON.stringify({
				"text": text,
				"target_lang": target_lang,
				"source_lang": source_lang
			}),
		});
		if (!response.ok) return text;
		const json = await response.json();
		return json['text'] || text;
	} catch {
		// Translation is best-effort; fall back to the original text.
		return text;
	}
}

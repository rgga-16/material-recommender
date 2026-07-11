/**
 * Central client-server helpers: JSON fetch with error extraction, image
 * URL derivation, chat session id, and SSE-over-POST streaming.
 */

/** POST a JSON body and return the parsed JSON response.
 * Throws an Error carrying the server's {error} message on non-2xx. */
export async function postJson(url, body) {
	const response = await fetch(url, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(body ?? {}),
	});
	if (!response.ok) {
		const err_json = await response.json().catch(() => ({}));
		throw new Error(err_json.error || `Request failed (${response.status})`);
	}
	return response.json();
}

/**
 * Turn a server-provided image path (public URL like
 * "gen_images/renderings/current/wood_0.png") into a browser-loadable src.
 * data:/blob:/http(s): values pass through untouched.
 * With {bust: true} a cache-busting query is appended — use it for files the
 * server overwrites in place (generated textures, current-scene maps).
 */
export function imageUrl(path, { bust = false } = {}) {
	if (!path || /^(data:|blob:|https?:)/.test(path)) return path;
	const url = encodeURI('/' + String(path).replace(/\\/g, '/').replace(/^\/+/, ''));
	return bust ? `${url}?v=${Date.now()}` : url;
}

/** Stable per-browser-tab chat session id (so each tab gets its own
 * conversation history on the server). */
export function sessionId() {
	let id = sessionStorage.getItem('chat_session_id');
	if (!id) {
		id = (crypto.randomUUID && crypto.randomUUID()) ||
			`s-${Date.now()}-${Math.random().toString(36).slice(2)}`;
		sessionStorage.setItem('chat_session_id', id);
	}
	return id;
}

/**
 * POST to an SSE endpoint (e.g. /query_stream) and consume the event stream.
 * Events are JSON: {delta} chunks, then {done}, or {error}.
 * onDelta(chunk, fullTextSoFar) fires per chunk; resolves with the full text.
 */
export async function streamChat(url, body, { onDelta } = {}) {
	const response = await fetch(url, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(body ?? {}),
	});
	if (!response.ok || !response.body) {
		const err_json = await response.json().catch(() => ({}));
		throw new Error(err_json.error || `Request failed (${response.status})`);
	}

	const reader = response.body.getReader();
	const decoder = new TextDecoder();
	let buffer = '';
	let full = '';
	for (;;) {
		const { done, value } = await reader.read();
		if (done) break;
		buffer += decoder.decode(value, { stream: true });
		let sep;
		while ((sep = buffer.indexOf('\n\n')) !== -1) {
			const rawEvent = buffer.slice(0, sep);
			buffer = buffer.slice(sep + 2);
			const dataLine = rawEvent.split('\n').find((l) => l.startsWith('data: '));
			if (!dataLine) continue;
			const event = JSON.parse(dataLine.slice(6));
			if (event.error) throw new Error(event.error);
			if (event.delta) {
				full += event.delta;
				if (onDelta) onDelta(event.delta, full);
			}
		}
	}
	return full;
}

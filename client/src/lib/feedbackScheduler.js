// Proactive design feedback: runs /feedback_scene in the background after
// meaningful scene changes (debounced) and on an idle interval, but only when
// the scene actually changed since the last critique. Results land in the
// feedback_feed store, bump the rail badge, and raise a clickable toast.
//
// Pacing comes from the server (GET /app_config): FEEDBACK_DEBOUNCE_S after
// the last change, FEEDBACK_MIN_INTERVAL_S floor between runs.
import { get } from 'svelte/store';
import {
	action_history,
	curr_texture_parts,
	feedback_feed,
	feedback_unread,
	in_japanese,
	use_chatgpt,
} from '../stores.js';
import { viewport } from './registry.js';
import { postJson } from './api.js';
import { pollJob } from './jobs.js';
import { showToast } from './toast.js';

let debounce_ms = 20 * 1000;
let min_interval_ms = 180 * 1000;
const IDLE_CHECK_MS = 30 * 1000;

let started = false;
let running = false;
let debounce_timer = null;
let idle_timer = null;
let last_run_at = 0;
let last_critiqued_state = null;
let open_panel = () => {};
let unsubscribe_history = null;

/** Stable fingerprint of everything feedback would comment on. */
function sceneState() {
	const parts = get(curr_texture_parts) || {};
	const state = [];
	for (const obj of Object.keys(parts).sort()) {
		for (const part of Object.keys(parts[obj]).sort()) {
			const entry = parts[obj][part];
			if (!entry || typeof entry !== 'object') continue;
			state.push([obj, part, entry['mat_name'], entry['color'],
				entry['roughness'], entry['metalness']]);
		}
	}
	return state.length > 0 ? JSON.stringify(state) : null;
}

async function loadConfig() {
	try {
		const config = await (await fetch('/app_config')).json();
		if (config['feedback_debounce_s'] > 0) debounce_ms = config['feedback_debounce_s'] * 1000;
		if (config['feedback_min_interval_s'] > 0) min_interval_ms = config['feedback_min_interval_s'] * 1000;
	} catch {
		// Defaults stand.
	}
}

function scheduleAfterChange() {
	clearTimeout(debounce_timer);
	debounce_timer = setTimeout(() => run(), debounce_ms);
}

function onIdleCheck() {
	if (Date.now() - last_run_at < min_interval_ms) return;
	run();
}

async function run() {
	if (running || !get(use_chatgpt)) return;
	const state = sceneState();
	if (!state || state === last_critiqued_state) return;

	running = true;
	last_run_at = Date.now();

	let screenshot = null;
	try {
		screenshot = viewport.get()?.captureScreenshot(1) ?? null;
	} catch (error) {
		console.warn('scene screenshot unavailable for feedback', error);
	}

	try {
		const submit = await postJson('/feedback_scene', { screenshot });
		const data = await pollJob(submit.job_id);
		if (!data?.summary && !(data?.observations?.length > 0)) return;

		last_critiqued_state = state;
		feedback_feed.update((feed) => [{
			id: `${Date.now()}`,
			at: new Date(),
			summary: data['summary'] || '',
			observations: data['observations'] || [],
			references: data['references'] || '',
		}, ...feed]);
		feedback_unread.update((n) => n + 1);

		const japanese = get(in_japanese);
		showToast(
			japanese
				? '新しいデザインフィードバックがあります — クリックして表示'
				: 'New design feedback on your scene — click to view',
			'info', 8000, () => open_panel());
	} catch (error) {
		// Feedback is best-effort background work; never toast an error.
		console.warn('scene feedback failed', error);
	} finally {
		running = false;
	}
}

/** Start the scheduler (idempotent). openPanel opens the Feedback rail tab. */
export function startFeedbackScheduler({ openPanel } = {}) {
	if (started) return;
	started = true;
	if (openPanel) open_panel = openPanel;

	loadConfig();

	let last_action_count = get(action_history)?.actions?.length ?? 0;
	unsubscribe_history = action_history.subscribe((history) => {
		const count = history?.actions?.length ?? 0;
		if (count > last_action_count) scheduleAfterChange();
		last_action_count = count;
	});

	idle_timer = setInterval(onIdleCheck, IDLE_CHECK_MS);
}

export function stopFeedbackScheduler() {
	started = false;
	clearTimeout(debounce_timer);
	clearInterval(idle_timer);
	unsubscribe_history?.();
	unsubscribe_history = null;
}

/** Testing hooks. */
export const _internals = {
	sceneState,
	run,
	setPacing(debounceMs, minIntervalMs) {
		debounce_ms = debounceMs;
		min_interval_ms = minIntervalMs;
	},
	reset() {
		last_critiqued_state = null;
		last_run_at = 0;
		running = false;
	},
};

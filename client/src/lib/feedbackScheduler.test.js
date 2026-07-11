import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { get } from 'svelte/store';

vi.mock('./api.js', () => ({
	postJson: vi.fn(async () => ({ job_id: 'job-1' })),
}));
vi.mock('./jobs.js', () => ({
	pollJob: vi.fn(async () => ({
		summary: 'Looks coastal.',
		observations: [{ aspect: 'brief alignment', text: 'On brief.', suggestions: [] }],
		references: '',
	})),
}));

import { postJson } from './api.js';
import { _internals } from './feedbackScheduler.js';
import { curr_texture_parts, feedback_feed, feedback_unread, use_chatgpt } from '../stores.js';

// Node has no canvas/viewport; the scheduler treats a missing viewport as
// "no screenshot" and proceeds.

const SCENE = {
	chair: {
		seat: { mat_name: 'teak', color: '#FFFFFF', roughness: 0.5, metalness: 0 },
	},
};

beforeEach(() => {
	feedback_feed.set([]);
	feedback_unread.set(0);
	use_chatgpt.set(true);
	curr_texture_parts.set(SCENE);
	_internals.setPacing(10, 10);
	_internals.reset();
	vi.stubGlobal('fetch', vi.fn(async () => ({ json: async () => ({}) })));
});

afterEach(() => {
	vi.unstubAllGlobals();
	vi.clearAllMocks();
});

describe('feedback scheduler', () => {
	it('fingerprints the scene from material-relevant fields only', () => {
		const state = _internals.sceneState();
		expect(state).toContain('teak');
		curr_texture_parts.set({});
		expect(_internals.sceneState()).toBeNull();
		curr_texture_parts.set(SCENE);
		expect(_internals.sceneState()).toBe(state);
	});

	it('runs feedback and appends to the feed with an unread bump', async () => {
		await _internals.run();
		expect(postJson).toHaveBeenCalledWith('/feedback_scene', { screenshot: null });
		const feed = get(feedback_feed);
		expect(feed).toHaveLength(1);
		expect(feed[0].summary).toBe('Looks coastal.');
		expect(get(feedback_unread)).toBe(1);
	});

	it('skips when the scene has not changed since the last critique', async () => {
		await _internals.run();
		await _internals.run();
		expect(postJson).toHaveBeenCalledTimes(1);
	});

	it('runs again after a scene change', async () => {
		await _internals.run();
		curr_texture_parts.set({
			chair: { seat: { mat_name: 'chrome', color: '#FFFFFF', roughness: 0.2, metalness: 0.9 } },
		});
		await _internals.run();
		expect(postJson).toHaveBeenCalledTimes(2);
		expect(get(feedback_feed)).toHaveLength(2);
	});

	it('does nothing when the assistant is disabled', async () => {
		use_chatgpt.set(false);
		curr_texture_parts.set({
			chair: { seat: { mat_name: 'linen', color: '#EEEEEE', roughness: 0.9, metalness: 0 } },
		});
		await _internals.run();
		expect(postJson).not.toHaveBeenCalled();
	});
});

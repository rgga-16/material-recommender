import { afterEach, describe, expect, it, vi } from 'vitest';
import { pollJob } from './jobs.js';

// Node has no EventSource, so pollJob exercises its polling fallback here.

afterEach(() => {
	vi.unstubAllGlobals();
});

function fetchReturning(bodies) {
	let call = 0;
	return vi.fn(async () => {
		const body = bodies[Math.min(call, bodies.length - 1)];
		call += 1;
		return { ok: true, json: async () => body };
	});
}

describe('pollJob (polling fallback)', () => {
	it('resolves with job.result when done', async () => {
		vi.stubGlobal('fetch', fetchReturning([
			{ status: 'running', progress: 0.4, message: 'working' },
			{ status: 'done', result: { textures: 2 } },
		]));
		const progress = [];
		const result = await pollJob('abc', { interval: 1, onProgress: (j) => progress.push(j.status) });
		expect(result).toEqual({ textures: 2 });
		expect(progress).toEqual(['running', 'done']);
	});

	it('rejects with the job error', async () => {
		vi.stubGlobal('fetch', fetchReturning([{ status: 'error', error: 'boom' }]));
		await expect(pollJob('abc', { interval: 1 })).rejects.toThrow('boom');
	});

	it('rejects on http failure', async () => {
		vi.stubGlobal('fetch', vi.fn(async () => ({ ok: false, status: 404 })));
		await expect(pollJob('abc', { interval: 1 })).rejects.toThrow('404');
	});
});

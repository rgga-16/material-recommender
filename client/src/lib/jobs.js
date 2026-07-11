/**
 * Follows a background job until it finishes.
 *
 * Primary transport is Server-Sent Events (GET /jobs/<id>/events), which
 * pushes every status/progress change with no polling. If the stream can't
 * be established or drops before the job finishes, falls back to polling
 * GET /jobs/<id>.
 *
 * @param {string} job_id
 * @param {{interval?: number, onProgress?: (job: object) => void}} options
 * @returns {Promise<any>} Resolves with job.result when status is 'done'.
 *   Rejects with an Error when status is 'error'.
 */
export function pollJob(job_id, { interval = 750, onProgress } = {}) {
	return new Promise((resolve, reject) => {
		let settled = false;

		function handleJob(job) {
			if (onProgress) onProgress(job);
			if (job.status === 'done') {
				settled = true;
				resolve(job.result);
				return true;
			}
			if (job.status === 'error') {
				settled = true;
				reject(new Error(job.error));
				return true;
			}
			return false;
		}

		function startPolling() {
			async function tick() {
				try {
					const response = await fetch(`/jobs/${job_id}`);
					if (!response.ok) throw new Error(`job lookup failed (${response.status})`);
					if (!handleJob(await response.json())) setTimeout(tick, interval);
				} catch (error) {
					settled = true;
					reject(error);
				}
			}
			tick();
		}

		if (typeof EventSource === 'undefined') {
			startPolling();
			return;
		}

		const source = new EventSource(`/jobs/${job_id}/events`);
		source.onmessage = (event) => {
			try {
				if (handleJob(JSON.parse(event.data))) source.close();
			} catch {
				// malformed event; the next one (or the fallback) will recover
			}
		};
		source.addEventListener('gone', () => {
			source.close();
			if (!settled) {
				settled = true;
				reject(new Error('unknown job'));
			}
		});
		source.onerror = () => {
			source.close();
			if (!settled) startPolling();
		};
	});
}

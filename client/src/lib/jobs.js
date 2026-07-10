/**
 * Polls GET /jobs/<job_id> until the job's status is 'done' or 'error'.
 * @param {string} job_id
 * @param {{interval?: number, onProgress?: (job: object) => void}} options
 * @returns {Promise<any>} Resolves with job.result when status is 'done'. Rejects with an Error when status is 'error'.
 */
export function pollJob(job_id, { interval = 750, onProgress } = {}) {
	return new Promise((resolve, reject) => {
		async function tick() {
			try {
				const response = await fetch(`/jobs/${job_id}`);
				const job = await response.json();

				if (onProgress) {
					onProgress(job);
				}

				if (job.status === 'done') {
					resolve(job.result);
				} else if (job.status === 'error') {
					reject(new Error(job.error));
				} else {
					setTimeout(tick, interval);
				}
			} catch (error) {
				reject(error);
			}
		}
		tick();
	});
}

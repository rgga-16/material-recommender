import { toasts } from '../stores.js';

let toast_id_counter = 0;

/**
 * Pushes a toast notification onto the toasts store and auto-removes it after `duration` ms.
 * @param {string} message - The message to display.
 * @param {'info'|'success'|'error'} type - The type of toast (controls color).
 * @param {number} duration - How long (in ms) the toast stays visible before auto-dismissing.
 * @param {() => void} [onClick] - Optional action run when the toast is clicked (before dismissal).
 */
export function showToast(message, type = 'info', duration = 4000, onClick = null) {
	const id = ++toast_id_counter;
	toasts.update(current => [...current, { id, message, type, onClick }]);

	if (duration > 0) {
		setTimeout(() => {
			toasts.update(current => current.filter(t => t.id !== id));
		}, duration);
	}

	return id;
}

// Imperative-call surfaces for the three components other modules need to poke
// (3D viewport, inspector, texture generator). Replaces the old anti-pattern of
// storing component instances in writable stores, which does not survive the
// Svelte 5 runes migration. Providers call `register(fns)` during init and clean
// up with the returned function (wire it through onDestroy); callers use
// `surface.get()?.fn(...)`.

function surface(name) {
	let impl = null;
	return {
		register(fns) {
			impl = fns;
			return () => {
				if (impl === fns) impl = null;
			};
		},
		get() {
			if (!impl) console.warn(`registry: "${name}" is not mounted`);
			return impl;
		},
	};
}

export const viewport = surface('viewport'); // provided by ThreeDDisplay.svelte
export const inspector = surface('inspector'); // provided by InformationPanel.svelte
export const generator = surface('generator'); // provided by GenerationModule/Generate.svelte

import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

const FLASK = 'http://localhost:2099';

// Every server-owned path: API endpoints plus asset dirs Flask writes/serves at
// runtime (gen_images, preset_materials, models). Keeps dev on :5173 CORS-free.
const proxyPaths = [
	'/get_current_rendering', '/get_saved_renderings', '/save_rendering',
	'/apply_to_current_rendering', '/get_image', '/transfer_texture', '/upload_model',
	'/update_manifest', '/remove_object', '/update_transforms', '/generate_textures',
	'/generate_similar_textures', '/jobs', '/get_preset_materials', '/api',
	'/init_query', '/query', '/translate', '/suggest_materials', '/suggest_colors',
	'/get_texture_prompts', '/get_materials', '/feedback_materials',
	'/brainstorm_prompt_keywords', '/brainstorm_material_queries',
	'/add_old_and_new_textures_to_action_history', '/retrieve_textures_from_action_history',
	'/generated_textures', '/export_texture_set', '/hdri_list', '/hdri',
	'/gen_images', '/preset_materials', '/models',
];

export default defineConfig({
	plugins: [svelte()],
	// public/ is Flask's static root AND our build target; static/ holds
	// build-time assets (favicon, logos) that Vite copies into public/.
	publicDir: 'static',
	server: {
		port: 5173,
		proxy: Object.fromEntries(proxyPaths.map((p) => [p, FLASK])),
		// OneDrive breaks native file watching; public/ churns with generated images.
		watch: { ignored: ['**/public/**'], usePolling: true },
	},
	build: {
		outDir: 'public',
		// CRITICAL: never empty public/ — Flask writes gen_images/ into it at runtime.
		emptyOutDir: false,
		sourcemap: true,
	},
});

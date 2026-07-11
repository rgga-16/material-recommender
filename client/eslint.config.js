import js from '@eslint/js';
import svelte from 'eslint-plugin-svelte';
import prettier from 'eslint-config-prettier';
import globals from 'globals';

export default [
	{ ignores: ['public/', 'node_modules/', 'static/', 'dist/'] },
	js.configs.recommended,
	...svelte.configs['flat/recommended'],
	prettier,
	...svelte.configs['flat/prettier'],
	{
		languageOptions: {
			globals: { ...globals.browser },
		},
		rules: {
			// This is a research codebase: console diagnostics are fine, and
			// unused function args often document callback signatures.
			'no-unused-vars': ['warn', { args: 'none', varsIgnorePattern: '^_' }],
			'no-empty': ['warn', { allowEmptyCatch: true }],
			// Pre-existing unkeyed each blocks: keying them blindly changes
			// reconciliation behavior, so surface as warnings to fix case by case.
			'svelte/require-each-key': 'warn',
			'svelte/prefer-writable-derived': 'warn',
		},
	},
];

<script>
	import { onDestroy, onMount } from 'svelte';
	import GeneratedTextures from './GeneratedTextures.svelte';
	import { generate_tab_page } from '../../stores.js';
	import { generated_texture_name } from '../../stores.js';
	import { in_japanese } from '../../stores.js';

	import { translate } from '../../lib/i18n.js';
	import { isDict, dictToString } from '../../lib/utils.js';
	import { showToast } from '../../lib/toast.js';
	import { pollJob } from '../../lib/jobs.js';

	import { generator } from '../../lib/registry.js';

	import Button from '../../lib/ui/Button.svelte';
	import Field from '../../lib/ui/Field.svelte';
	import TextInput from '../../lib/ui/TextInput.svelte';
	import NumberInput from '../../lib/ui/NumberInput.svelte';
	import Spinner from '../../lib/ui/Spinner.svelte';

	import Sparkles from '@lucide/svelte/icons/sparkles';
	import RefreshCw from '@lucide/svelte/icons/refresh-cw';

	onDestroy(generator.register({ generate_textures, reset_page }));


	let japanese = $derived($in_japanese);

	let input_material = $state('');

	let is_loading = $state(false);
	let progress_message = $state('');
	let generated_textures = $state([]);
	let selected_texture = $state(null);

	let n_textures = $state(4);
	// -1 = random; any other value makes generations reproducible (image i
	// uses seed + i).
	let seed = $state(-1);

	// Persistent gallery: previously generated textures survive restarts on
	// the server; show them until a fresh generation replaces them.
	let is_showing_gallery = $state(false);
	onMount(async () => {
		if (generated_textures.length > 0) return;
		try {
			const response = await fetch('/generated_textures');
			const data = await response.json();
			if (generated_textures.length === 0 && data['results']?.length > 0) {
				generated_textures = data['results'];
				is_showing_gallery = true;
			}
		} catch (error) {
			console.error('Could not load the generation gallery', error);
		}
	});

	// The material string is sent as-is: the server enriches it into a
	// detail-rich prompt (LLM + quality suffix), so no manual keywords needed.
	async function preparePrompt(texture_str) {
		let input = texture_str;
		if (isDict(input)) {
			input = dictToString(input);
		}
		if (japanese) {
			input = await translate('JA', 'EN-US', input);
		}
		return input;
	}

	async function generate_similar_textures(texture_str) {
		input_material = texture_str;
		is_loading = true;
		progress_message = '';
		is_showing_gallery = false;
		generated_textures = [];

		const input = await preparePrompt(texture_str);

		try {
			const results_response = await fetch('/generate_similar_textures', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					texture_string: input,
					n: n_textures,
					imsize: 448,
					impath: selected_texture,
					seed: seed,
				}),
			});
			selected_texture = null;
			const results_json = await results_response.json();

			let result;
			if (results_json && results_json['job_id']) {
				// Backend is async: poll the job until it's done, then use its result payload.
				result = await pollJob(results_json['job_id'], {
					onProgress: (job) => {
						progress_message = job.message || '';
					},
				});
			} else {
				// Backend responded synchronously with the results directly.
				result = results_json;
			}

			generated_textures = result['results'];
			generated_texture_name.set(input);
		} catch (error) {
			console.error(error);
			showToast(japanese ? 'テクスチャの生成中にエラーが発生しました。' : 'An error occurred while generating textures.', 'error');
		} finally {
			is_loading = false;
			progress_message = '';
		}
	}

	export async function generate_textures(texture_str) {
		input_material = texture_str;
		is_loading = true;
		progress_message = '';
		is_showing_gallery = false;
		selected_texture = null;
		generated_textures = [];

		const input = await preparePrompt(texture_str);

		try {
			const results_response = await fetch('/generate_textures', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					texture_string: input,
					n: n_textures,
					imsize: 448,
					seed: seed,
				}),
			});

			const results_json = await results_response.json();

			let result;
			if (results_json && results_json['job_id']) {
				// Backend is async: poll the job until it's done, then use its result payload.
				result = await pollJob(results_json['job_id'], {
					onProgress: (job) => {
						progress_message = job.message || '';
					},
				});
			} else {
				// Backend responded synchronously with the results directly.
				result = results_json;
			}

			generated_textures = result['results'];
			generated_texture_name.set(input);
		} catch (error) {
			console.error(error);
			showToast(japanese ? 'テクスチャの生成中にエラーが発生しました。' : 'An error occurred while generating textures.', 'error');
		} finally {
			is_loading = false;
			progress_message = '';
		}
	}

	// This function reverts back to the first page of the Generation module.
	export function reset_page() {
		generate_tab_page.set(0);
		generated_textures = [];
		selected_texture = null;
	}
</script>

<div class="generate-panel" class:hidden={$generate_tab_page !== 0}>
	<h3 class="panel-title">{japanese ? '素材ジェネレーター' : 'Material Generator'}</h3>

	<TextInput
		bind:value={input_material}
		onEnter={() => generate_textures(input_material)}
		placeholder={japanese ? '素材を入力してください...' : 'Type in a material, e.g. "wood"...'}
	/>
	<p class="input-hint">
		{japanese
			? 'アシスタントがデザインブリーフに沿ってプロンプトを自動的に詳細化します。'
			: 'The assistant automatically enriches your material into a detailed prompt using the design brief.'}
	</p>

	<Field label={japanese ? 'テクスチャマップの数：' : 'No. of texture maps:'} row>
		<NumberInput bind:value={n_textures} min={1} max={10} step={1} />
	</Field>

	<Field label={japanese ? 'シード（-1 = ランダム）：' : 'Seed (-1 = random):'} row>
		<NumberInput bind:value={seed} min={-1} step={1} />
	</Field>

	<div class="actions-row">
		<Button variant="secondary" disabled={!selected_texture} onclick={() => generate_similar_textures(input_material)}>
			<RefreshCw size={14} strokeWidth={1.75} />
			{japanese ? '類似素材テクスチャを生成する' : 'Generate Similar Textures'}
		</Button>
		<Button variant="primary" loading={is_loading} onclick={() => generate_textures(input_material)}>
			<Sparkles size={14} strokeWidth={1.75} />
			{japanese ? '素材テクスチャを生成する' : 'Generate Textures'}
		</Button>
	</div>

	{#if is_loading && progress_message}
		<div class="status-line">{progress_message}</div>
	{/if}

	<div class="results">
		{#if generated_textures.length > 0}
			<p class="results-caption">
				{#if is_showing_gallery}
					{japanese ? '以前に生成されたテクスチャ' : 'Previously generated textures'}
				{:else if japanese}
					{input_material}のテクスチャマップの結果
				{:else}
					Texture map results for: {input_material}
				{/if}
			</p>
			<GeneratedTextures pairs={generated_textures} texture_name={$generated_texture_name} bind:selected_texture />
		{:else if is_loading}
			<div class="empty-state">
				<Spinner size={32} />
				<span>{japanese ? 'テクスチャを生成しています。お待ちください。' : 'Generating textures, please wait.'}</span>
			</div>
		{:else}
			<div class="empty-state">
				<span>{japanese ? '素材テクスチャはまだ生成されていない。' : 'No material textures generated yet.'}</span>
			</div>
		{/if}
	</div>
</div>

<style>
	.generate-panel {
		display: flex;
		flex-direction: column;
		gap: var(--sp-3);
		width: 100%;
		height: 100%;
		min-height: 0;
	}

	.generate-panel.hidden {
		display: none;
	}

	.panel-title {
		margin: 0;
		font-size: var(--text-sm);
		font-weight: 600;
		color: var(--text-primary);
	}

	.input-hint {
		margin: 0;
		font-size: var(--text-xs);
		color: var(--text-muted);
	}

	.actions-row {
		display: flex;
		gap: var(--sp-2);
	}

	.actions-row > :global(.btn) {
		flex: 1;
	}

	.status-line {
		font-size: var(--text-xs);
		color: var(--text-secondary);
	}

	.results {
		flex: 1;
		min-height: 0;
		display: flex;
		flex-direction: column;
		gap: var(--sp-2);
		overflow: auto;
	}

	.results-caption {
		margin: 0;
		font-size: var(--text-xs);
		color: var(--text-secondary);
	}

	.empty-state {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: var(--sp-2);
		color: var(--text-muted);
		font-size: var(--text-base);
		text-align: center;
	}
</style>

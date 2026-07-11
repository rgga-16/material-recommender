<script>
	import { onDestroy, onMount } from 'svelte';
	import GeneratedTextures from './GeneratedTextures.svelte';
	import { generate_tab_page } from '../../stores.js';
	import { generated_texture_name } from '../../stores.js';
	import { in_japanese } from '../../stores.js';
	import { design_brief } from '../../stores.js';

	import { translate } from '../../lib/i18n.js';
	import { isDict, dictToString } from '../../lib/utils.js';
	import { showToast } from '../../lib/toast.js';
	import { pollJob } from '../../lib/jobs.js';

	import { generator } from '../../lib/registry.js';

	import Button from '../../lib/ui/Button.svelte';
	import Field from '../../lib/ui/Field.svelte';
	import TextInput from '../../lib/ui/TextInput.svelte';
	import NumberInput from '../../lib/ui/NumberInput.svelte';
	import PanelSection from '../../lib/ui/PanelSection.svelte';
	import Spinner from '../../lib/ui/Spinner.svelte';

	import Sparkles from '@lucide/svelte/icons/sparkles';
	import RefreshCw from '@lucide/svelte/icons/refresh-cw';
	import Lightbulb from '@lucide/svelte/icons/lightbulb';
	import Plus from '@lucide/svelte/icons/plus';
	import X from '@lucide/svelte/icons/x';

	onDestroy(generator.register({ generate_textures, reset_page, empty_keywordlists }));


	let japanese = $derived($in_japanese);

	let input_material = $state('');

	let is_loading = $state(false);
	let progress_message = $state('');
	let generated_textures = $state([]);
	let selected_texture = $state(null);

	let keywords_open = $state(false);

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

	async function generate_similar_textures(texture_str) {
		input_material = texture_str;
		is_loading = true;
		progress_message = '';
		is_showing_gallery = false;
		generated_textures = [];

		let input = Object.assign('', texture_str);
		let material = Object.assign('', texture_str);
		if (isDict(input)) {
			input = dictToString(input);
		}

		let keywords = Object.assign([], selected_prompt_keywords);

		if (keywords.length > 0) {
			for (let i = 0; i < keywords.length; i++) {
				let temp = keywords[i];
				if (isDict(temp)) {
					temp = dictToString(temp);
					material = dictToString(material);
				}
				input += ', ' + temp;
			}
		}
		if (japanese) {
			console.log(input);
			input = await translate('JA', 'EN-US', input);
			material = await translate('JA', 'EN-US', material);
		}
		input += ',  texture map, seamless, 4k';
		console.log(input);

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
			generated_texture_name.set(material);
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

		let input = Object.assign('', texture_str);
		let material = Object.assign('', texture_str);
		if (isDict(input)) {
			input = dictToString(input);
			material = dictToString(material);
		}

		console.log(input);
		let keywords = Object.assign([], selected_prompt_keywords);

		if (keywords.length > 0) {
			for (let i = 0; i < keywords.length; i++) {
				let temp = keywords[i];
				if (isDict(temp)) {
					temp = dictToString(temp);
				}
				input += ', ' + temp;
			}
		}

		if (japanese) {
			console.log(input);
			input = await translate('JA', 'EN-US', input);
			material = await translate('JA', 'EN-US', material);
		}
		input += ',  texture map, seamless, 4k';
		console.log(input);

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
			generated_texture_name.set(material);
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

	let brainstormed_prompt_keywords = $state([]); // Keywords that are generated by the AI assistant
	let manual_prompt_keywords = $state([]); // Keywords that the user manually added

	let selected_prompt_keywords = $state([]);
	let is_loading_keywords = $state(false);

	let keyword = $state('');

	let keywords_title = $derived(
		japanese
			? `"${input_material.trim() !== '' ? input_material : ''}"にキーワードを追加`
			: `Add keywords to "${input_material.trim() !== '' ? input_material : ''}"`
	);

	export function empty_keywordlists() {
		keyword = '';
		brainstormed_prompt_keywords = [];
		manual_prompt_keywords = [];
		selected_prompt_keywords = [];
	}

	function toggle_keyword(word) {
		if (selected_prompt_keywords.includes(word)) {
			selected_prompt_keywords = selected_prompt_keywords.filter((k) => k !== word);
		} else {
			selected_prompt_keywords = [...selected_prompt_keywords, word];
		}
	}

	function del_manual_keyword(index, word) {
		manual_prompt_keywords.splice(index, 1);
		selected_prompt_keywords = selected_prompt_keywords.filter((k) => k !== word);
	}

	function del_brainstormed_keyword(index, word) {
		brainstormed_prompt_keywords.splice(index, 1);
		selected_prompt_keywords = selected_prompt_keywords.filter((k) => k !== word);
	}

	function add_keyword(k) {
		if (k.trim() === '') {
			showToast(japanese ? 'キーワードを入力してください。' : 'Please type in a keyword.', 'error');
			return;
		}
		manual_prompt_keywords.push(k);
		selected_prompt_keywords.push(k);

		keyword = '';
	}

	async function brainstorm_prompt_keywords() {
		if (input_material.trim() === '') {
			showToast(japanese ? '素材を入力してください。' : 'Please type in a material.', 'error');
			return;
		}

		brainstormed_prompt_keywords = [];
		selected_prompt_keywords = [];
		is_loading_keywords = true;
		const response = await fetch('/brainstorm_prompt_keywords', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				texture_string: input_material,
				design_brief: $design_brief,
			}),
		});
		const json = await response.json();

		brainstormed_prompt_keywords = json['brainstormed_prompt_keywords'];

		if (japanese) {
			for (let i = 0; i < brainstormed_prompt_keywords.length; i++) {
				brainstormed_prompt_keywords[i] = await translate('EN', 'JA', brainstormed_prompt_keywords[i]);
			}
		}
		is_loading_keywords = false;
	}
</script>

<div class="generate-panel" class:hidden={$generate_tab_page !== 0}>
	<h3 class="panel-title">{japanese ? '素材ジェネレーター' : 'Material Generator'}</h3>

	<TextInput
		bind:value={input_material}
		onEnter={() => generate_textures(input_material)}
		placeholder={japanese ? '素材を入力してください...' : 'Type in a material...'}
	/>

	<Field label={japanese ? 'テクスチャマップの数：' : 'No. of texture maps:'} row>
		<NumberInput bind:value={n_textures} min={1} max={10} step={1} />
	</Field>

	<Field label={japanese ? 'シード（-1 = ランダム）：' : 'Seed (-1 = random):'} row>
		<NumberInput bind:value={seed} min={-1} step={1} />
	</Field>

	<PanelSection title={keywords_title} bind:open={keywords_open}>
		<div class="keyword-input-row">
			<TextInput
				bind:value={keyword}
				onEnter={() => add_keyword(keyword)}
				placeholder={japanese ? 'キーワードを入力してください...' : 'Type in a keyword...'}
			/>
			<Button size="sm" onclick={() => add_keyword(keyword)}>
				<Plus size={14} strokeWidth={1.75} />
				{japanese ? '追加' : 'Add'}
			</Button>
		</div>

		<div class="keyword-actions-row">
			<Button size="sm" variant="secondary" onclick={brainstorm_prompt_keywords} disabled={is_loading_keywords}>
				<Lightbulb size={14} strokeWidth={1.75} />
				{#if japanese}
					"{input_material}"のキーワードをブレインストーミングする
				{:else}
					Brainstorm keywords for "{input_material}"
				{/if}
			</Button>

			<Button size="sm" variant="ghost" onclick={() => empty_keywordlists()}>
				{japanese ? 'キーワードをクリアする' : 'Clear keywords'}
			</Button>
		</div>

		<div class="keyword-tags">
			{#each manual_prompt_keywords as manual_keyword, i (i)}
				<span class="tag" class:selected={selected_prompt_keywords.includes(manual_keyword)}>
					<button type="button" class="tag-label" onclick={() => toggle_keyword(manual_keyword)}>
						"{manual_keyword}"
					</button>
					<button
						type="button"
						class="tag-remove"
						onclick={() => del_manual_keyword(i, manual_keyword)}
						aria-label={japanese ? '削除' : 'Remove keyword'}
					>
						<X size={12} strokeWidth={2} />
					</button>
				</span>
			{/each}

			{#if brainstormed_prompt_keywords.length > 0}
				{#each brainstormed_prompt_keywords as bkeyword, j (j)}
					<span class="tag" class:selected={selected_prompt_keywords.includes(bkeyword)}>
						<button type="button" class="tag-label" onclick={() => toggle_keyword(bkeyword)}>
							"{bkeyword}"
						</button>
						<button
							type="button"
							class="tag-remove"
							onclick={() => del_brainstormed_keyword(j, bkeyword)}
							aria-label={japanese ? '削除' : 'Remove keyword'}
						>
							<X size={12} strokeWidth={2} />
						</button>
					</span>
				{/each}
			{:else if is_loading_keywords}
				<div class="keywords-loading">
					<Spinner size={16} />
					{japanese ? 'キーワードを考える' : 'Brainstorming keywords...'}
				</div>
			{/if}

			{#if brainstormed_prompt_keywords.length <= 0 && manual_prompt_keywords.length <= 0 && !is_loading_keywords}
				<p class="empty-hint">{japanese ? 'キーワードは追加されていない。' : 'No keywords added.'}</p>
			{/if}
		</div>
	</PanelSection>

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

	.keyword-input-row {
		display: flex;
		align-items: center;
		gap: var(--sp-2);
	}

	.keyword-input-row > :global(.text-input) {
		flex: 1;
		min-width: 0;
	}

	.keyword-actions-row {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: var(--sp-2);
		margin-top: var(--sp-2);
	}

	.keyword-tags {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: var(--sp-2);
		margin-top: var(--sp-3);
	}

	.tag {
		display: inline-flex;
		align-items: center;
		gap: var(--sp-1);
		height: 24px;
		padding: 0 var(--sp-1) 0 var(--sp-3);
		border-radius: var(--radius-full);
		background: var(--bg-inset);
		border: 1px solid var(--border-subtle);
		color: var(--text-secondary);
		transition:
			border-color 120ms ease,
			background 120ms ease,
			color 120ms ease;
	}

	.tag:hover {
		border-color: var(--border-strong);
	}

	.tag.selected {
		border-color: var(--accent);
		background: var(--accent-muted);
		color: var(--text-primary);
	}

	.tag-label {
		background: transparent;
		border: none;
		padding: 0;
		font-family: var(--font-sans);
		font-size: var(--text-xs);
		color: inherit;
		cursor: pointer;
	}

	.tag-remove {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 18px;
		height: 18px;
		flex-shrink: 0;
		border: none;
		border-radius: var(--radius-full);
		background: transparent;
		color: var(--text-muted);
		cursor: pointer;
		transition:
			background 120ms ease,
			color 120ms ease;
	}

	.tag-remove:hover {
		background: var(--bg-hover);
		color: var(--text-primary);
	}

	.empty-hint {
		margin: 0;
		font-size: var(--text-xs);
		color: var(--text-muted);
	}

	.keywords-loading {
		display: flex;
		align-items: center;
		gap: var(--sp-2);
		font-size: var(--text-xs);
		color: var(--text-secondary);
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

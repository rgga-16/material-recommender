<script>
	// App shell (runes mode): top bar / icon rail / tool panel / 3D viewport /
	// inspector / saved-scenes shelf, laid out on a CSS grid with tokens from app.css.
	import { get } from 'svelte/store';
	import { onMount } from 'svelte';

	import ActionsPanel from './components/ActionsPanel.svelte';
	import ThreeDDisplay from './components/ThreeDDisplay.svelte';
	import Information from './components/InformationPanel.svelte';
	import Toast from './components/Toast.svelte';

	import Button from './lib/ui/Button.svelte';
	import IconButton from './lib/ui/IconButton.svelte';
	import Modal from './lib/ui/Modal.svelte';
	import Spinner from './lib/ui/Spinner.svelte';
	import Card from './lib/ui/Card.svelte';

	import Box from '@lucide/svelte/icons/box';
	import Sparkles from '@lucide/svelte/icons/sparkles';
	import MessageSquare from '@lucide/svelte/icons/message-square';
	import MessageSquareQuote from '@lucide/svelte/icons/message-square-quote';
	import SwatchBook from '@lucide/svelte/icons/swatch-book';
	import Upload from '@lucide/svelte/icons/upload';
	import WandSparkles from '@lucide/svelte/icons/wand-sparkles';
	import Undo2 from '@lucide/svelte/icons/undo-2';
	import Redo2 from '@lucide/svelte/icons/redo-2';
	import Save from '@lucide/svelte/icons/save';
	import Download from '@lucide/svelte/icons/download';
	import FileText from '@lucide/svelte/icons/file-text';
	import Move from '@lucide/svelte/icons/move';
	import ChevronDown from '@lucide/svelte/icons/chevron-down';
	import Sun from '@lucide/svelte/icons/sun';
	import Moon from '@lucide/svelte/icons/moon';
	import Globe from '@lucide/svelte/icons/globe';
	import PanelRight from '@lucide/svelte/icons/panel-right';

	import {
		curr_rendering_path,
		curr_texture_parts,
		curr_textureparts_path,
		object_transforms,
		displayWidth,
		displayHeight,
		design_brief,
		in_japanese,
		use_chatgpt,
		action_history,
		actions_panel_tab,
		feedback_unread,
	} from './stores.js';

	import { undoAction, redoAction } from './lib/history.js';
	import { showToast } from './lib/toast.js';
	import { imageUrl } from './lib/api.js';
	import { startFeedbackScheduler } from './lib/feedbackScheduler.js';

	let japanese = $derived($in_japanese);
	let history = $derived($action_history);

	let saved_renderings = $state([]);
	let selected_saved_rendering_idx = $state(undefined);

	let is_loading_scene = $state(false);
	let is_saving_scene = $state(false);
	let is_loading_saved_renderings = $state(false);

	let information_panel = $state(null);
	let threed_display = $state(null);

	let show_design_brief = $state(false);
	let design_brief_text = $state('');
	let is_saving_brief = $state(false);
	let brief_pdf_input = $state(null);

	let move_mode = $state(false);
	let tool_panel_collapsed = $state(false);
	let inspector_collapsed = $state(false);
	let shelf_collapsed = $state(false);

	// ----------------------------------------------------------------- theme

	let theme = $state(localStorage.getItem('theme') || 'dark');
	$effect(() => {
		document.documentElement.dataset.theme = theme;
		localStorage.setItem('theme', theme);
	});

	// ------------------------------------------------------ HDRI environment

	let hdris = $state([]);
	let selected_hdri = $state('');

	async function loadHdris() {
		try {
			const response = await fetch('/hdri_list');
			hdris = (await response.json())['hdris'] || [];
		} catch {
			hdris = [];
		}
	}

	function applyEnvironment() {
		threed_display?.setEnvironment(selected_hdri ? `/hdri/${selected_hdri}` : null)
			.catch((error) => {
				console.error(error);
				showToast(japanese ? '環境の読み込みに失敗しました。' : 'Failed to load environment.', 'error');
			});
	}

	// ------------------------------------------------------------------ data

	async function getSavedRenderings() {
		const response = await fetch('/get_saved_renderings');
		const data = await response.json();
		saved_renderings = data['saved_renderings'];
		return data;
	}
	const saved_renderings_promise = getSavedRenderings();

	async function getInitialRendering() {
		const response = await fetch('/get_current_rendering');
		const data = await response.json();
		curr_rendering_path.set(data['rendering_path']);
		curr_texture_parts.set(data['texture_parts']);
		curr_textureparts_path.set(data['textureparts_path']);
		object_transforms.set(data['transforms'] || {});
		return data;
	}
	const promise = getInitialRendering();

	// ---------------------------------------------------------- design brief
	// The brief lives server-side (every assistant prompt is grounded in it);
	// the store is a synced read model for display.

	async function syncDesignBrief() {
		try {
			const data = await (await fetch('/design_brief')).json();
			if (data['brief']) {
				design_brief.set(data['brief']);
				design_brief_text = data['brief'];
			}
		} catch (error) {
			console.warn('could not load design brief from server', error);
		}
	}

	async function saveDesignBrief() {
		is_saving_brief = true;
		try {
			const response = await fetch('/design_brief', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ brief: design_brief_text }),
			});
			if (!response.ok) throw new Error((await response.json())['error'] || 'save failed');
			const data = await response.json();
			design_brief.set(data['brief']);
			design_brief_text = data['brief'];
			showToast(japanese ? 'デザインブリーフを保存しました。' : 'Design brief saved.', 'success');
		} catch (error) {
			console.error(error);
			showToast(japanese ? 'デザインブリーフの保存に失敗しました。' : 'Failed to save the design brief.', 'error');
		} finally {
			is_saving_brief = false;
		}
	}

	async function uploadBriefPdf(event) {
		const file = event.target.files?.[0];
		event.target.value = '';
		if (!file) return;
		is_saving_brief = true;
		try {
			const form = new FormData();
			form.append('file', file);
			const response = await fetch('/design_brief_pdf', { method: 'POST', body: form });
			const data = await response.json();
			if (!response.ok) throw new Error(data['error'] || 'PDF upload failed');
			design_brief.set(data['brief']);
			design_brief_text = data['brief'];
			showToast(japanese ? 'PDFからデザインブリーフを設定しました。' : 'Design brief set from PDF.', 'success');
		} catch (error) {
			console.error(error);
			showToast(error.message, 'error');
		} finally {
			is_saving_brief = false;
		}
	}

	async function saveRendering() {
		is_saving_scene = true;
		is_loading_saved_renderings = true;
		let thumbnail = null;
		try {
			threed_display.removeHighlights();
			thumbnail = threed_display.captureScreenshot(1);
		} catch (error) {
			console.error('Could not capture scene thumbnail', error);
		}
		const response = await fetch('/save_rendering', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				rendering_path: $curr_rendering_path,
				texture_parts: $curr_texture_parts,
				textureparts_path: $curr_textureparts_path,
				thumbnail: thumbnail,
			}),
		});
		const data = await response.json();
		selected_saved_rendering_idx = undefined;
		saved_renderings = data['saved_renderings'];
		is_loading_saved_renderings = false;
		is_saving_scene = false;
		showToast(japanese ? 'シーンを保存しました。' : 'Scene saved.', 'success');
	}

	async function loadRendering(idx) {
		if (idx == undefined || !saved_renderings[idx]) return;
		is_loading_scene = true;
		const selected = saved_renderings[idx];
		const response = await fetch('/apply_to_current_rendering', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				rendering_path: selected['rendering_path'],
				texture_parts: selected['texture_parts'],
				textureparts_path: selected['textureparts_path'],
			}),
		});
		const data = await response.json();
		curr_rendering_path.set(data['rendering_path']);
		curr_texture_parts.set(data['texture_parts']);
		curr_textureparts_path.set(data['textureparts_path']);
		object_transforms.set(data['transforms'] || {});
		threed_display.update_3d_scene();
		is_loading_scene = false;
	}

	// --------------------------------------------------------------- actions

	function exportImage() {
		try {
			threed_display.removeHighlights();
			const dataURL = threed_display.captureScreenshot(2);
			const link = document.createElement('a');
			link.href = dataURL;
			link.download = 'scene.png';
			link.click();
		} catch (error) {
			console.error(error);
			showToast(japanese ? '画像の書き出しに失敗しました。' : 'Failed to export image.', 'error');
		}
	}

	function toggleMoveMode() {
		move_mode = threed_display.setMoveMode(!move_mode);
	}

	// ------------------------------------------------------------------ rail

	const rail_items = [
		{ id: 'generate', icon: Sparkles, en: 'Generate', ja: '生成する' },
		{ id: 'chatbot', icon: MessageSquare, en: 'ChatBot', ja: 'チャットボット', gated: true },
		{ id: 'feedback', icon: MessageSquareQuote, en: 'Feedback', ja: 'フィードバック', gated: true },
		{ id: 'mat_lib', icon: SwatchBook, en: 'Material Library', ja: '素材ライブラリ' },
		{ id: 'upload', icon: Upload, en: 'Upload', ja: 'アップロード' },
		{ id: 'auto_style', icon: WandSparkles, en: 'Auto-Style', ja: '自動スタイル' },
	];

	function railClick(id) {
		if (id === 'feedback') feedback_unread.set(0);
		if ($actions_panel_tab === id && !tool_panel_collapsed) {
			tool_panel_collapsed = true;
		} else {
			tool_panel_collapsed = false;
			actions_panel_tab.set(id);
		}
	}

	function openFeedbackPanel() {
		feedback_unread.set(0);
		tool_panel_collapsed = false;
		actions_panel_tab.set('feedback');
	}

	let active_rail_item = $derived(rail_items.find((r) => r.id === $actions_panel_tab));

	// ------------------------------------------------------- viewport sizing

	let viewport_el = $state(null);

	// Ctrl+Z / Ctrl+Y (or Ctrl+Shift+Z) / Ctrl+S — skipped while typing.
	function onShortcut(event) {
		if (!(event.ctrlKey || event.metaKey)) return;
		const target = event.target;
		if (target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' ||
				target.isContentEditable)) return;
		const key = event.key.toLowerCase();
		if (key === 'z' && event.shiftKey) {
			event.preventDefault();
			redoAction();
		} else if (key === 'z') {
			event.preventDefault();
			undoAction();
		} else if (key === 'y') {
			event.preventDefault();
			redoAction();
		} else if (key === 's') {
			event.preventDefault();
			saveRendering();
		}
	}

	onMount(() => {
		design_brief_text = get(design_brief);
		syncDesignBrief();
		loadHdris();
		if (get(use_chatgpt)) {
			startFeedbackScheduler({ openPanel: openFeedbackPanel });
		}
		window.addEventListener('keydown', onShortcut);

		const observer = new ResizeObserver(() => {
			if (!viewport_el) return;
			displayWidth.set(viewport_el.offsetWidth);
			displayHeight.set(viewport_el.offsetHeight);
		});
		if (viewport_el) {
			displayWidth.set(viewport_el.offsetWidth);
			displayHeight.set(viewport_el.offsetHeight);
			observer.observe(viewport_el);
		}
		return () => {
			window.removeEventListener('keydown', onShortcut);
			observer.disconnect();
		};
	});
</script>

<Toast />

<div class="shell" class:tool-collapsed={tool_panel_collapsed} class:inspector-collapsed={inspector_collapsed} class:shelf-collapsed={shelf_collapsed}>
	<!-- ============================================================ top bar -->
	<header class="topbar">
		<div class="brand">
			<span class="brand-mark"><Box size={18} strokeWidth={1.75} /></span>
			<span class="brand-name">Texture Studio</span>
		</div>

		<div class="topbar-group">
			<Button size="sm" variant="ghost" onclick={saveRendering} loading={is_saving_scene}>
				<Save size={14} strokeWidth={1.75} />
				{japanese ? 'シーンを保存' : 'Save Scene'}
			</Button>
			<Button size="sm" variant="ghost" onclick={exportImage}>
				<Download size={14} strokeWidth={1.75} />
				{japanese ? '画像を書き出す' : 'Export PNG'}
			</Button>
			<Button size="sm" variant="ghost" onclick={() => (show_design_brief = true)}>
				<FileText size={14} strokeWidth={1.75} />
				{japanese ? 'デザイン概要' : 'Design Brief'}
			</Button>
		</div>

		<div class="topbar-spacer"></div>

		<div class="topbar-group">
			<IconButton
				label={history.currentIndex <= -1
					? japanese ? '元に戻す' : 'Undo'
					: (japanese ? '元に戻す: ' : 'Undo ') + history.actions[history.currentIndex]['name']}
				disabled={history.currentIndex <= -1}
				onclick={undoAction}
			>
				<Undo2 size={16} strokeWidth={1.75} />
			</IconButton>
			<IconButton
				label={japanese ? 'やり直す' : 'Redo'}
				disabled={history.currentIndex >= history.actions.length - 1}
				onclick={redoAction}
			>
				<Redo2 size={16} strokeWidth={1.75} />
			</IconButton>
		</div>

		{#if hdris.length > 0}
			<div class="env-picker" title={japanese ? '環境ライティング' : 'Environment lighting'}>
				<Globe size={14} strokeWidth={1.75} />
				<select bind:value={selected_hdri} onchange={applyEnvironment} aria-label={japanese ? '環境ライティング' : 'Environment lighting'}>
					<option value="">{japanese ? 'スタジオ（標準）' : 'Studio (default)'}</option>
					{#each hdris as hdri (hdri)}
						<option value={hdri}>{hdri.replace(/\.(exr|hdr)$/i, '')}</option>
					{/each}
				</select>
			</div>
		{/if}

		<IconButton
			label={theme === 'dark' ? (japanese ? 'ライトテーマ' : 'Light theme') : (japanese ? 'ダークテーマ' : 'Dark theme')}
			onclick={() => (theme = theme === 'dark' ? 'light' : 'dark')}
		>
			{#if theme === 'dark'}
				<Sun size={16} strokeWidth={1.75} />
			{:else}
				<Moon size={16} strokeWidth={1.75} />
			{/if}
		</IconButton>

		<div class="divider"></div>

		<div class="lang-toggle" role="group" aria-label="Language">
			<button class="lang-btn" class:active={!japanese} onclick={() => in_japanese.set(false)}>EN</button>
			<button class="lang-btn" class:active={japanese} onclick={() => in_japanese.set(true)}>日本語</button>
		</div>
	</header>

	<!-- =========================================================== icon rail -->
	<nav class="rail">
		{#each rail_items as item (item.id)}
			{#if !item.gated || $use_chatgpt}
				<div class="rail-item">
					<IconButton
						label={japanese ? item.ja : item.en}
						active={$actions_panel_tab === item.id && !tool_panel_collapsed}
						onclick={() => railClick(item.id)}
					>
						<item.icon size={20} strokeWidth={1.75} />
					</IconButton>
					{#if item.id === 'feedback' && $feedback_unread > 0}
						<span class="rail-badge">{$feedback_unread}</span>
					{/if}
				</div>
			{/if}
		{/each}
	</nav>

	<!-- ========================================================== tool panel -->
	<aside class="tool-panel" aria-hidden={tool_panel_collapsed}>
		<div class="tool-panel-header">
			{japanese ? active_rail_item?.ja : active_rail_item?.en}
		</div>
		<div class="tool-panel-body">
			<ActionsPanel />
		</div>
	</aside>

	<!-- ============================================================ viewport -->
	<section class="viewport" bind:this={viewport_el}>
		{#await promise}
			<div class="viewport-status">
				<Spinner size={28} />
				<span>{japanese ? '3Dビューアをロードしています…' : 'Loading 3D viewer…'}</span>
			</div>
		{:then}
			<ThreeDDisplay
				bind:this={threed_display}
				current_texture_parts={get(curr_texture_parts)}
			/>
			<div class="viewport-toolbar">
				<button
					class="mode-btn"
					class:active={move_mode}
					onclick={toggleMoveMode}
					title={japanese
						? 'オブジェクトをクリックして移動 (g/r/sキーで切替)'
						: 'Click an object to move it (g / r / s switch gizmo)'}
				>
					<Move size={14} strokeWidth={1.75} />
					{move_mode ? (japanese ? '移動モード: オン' : 'Move: ON') : japanese ? 'オブジェクトを移動' : 'Move Objects'}
				</button>
			</div>
			<div class="inspector-toggle">
				<IconButton
					label={inspector_collapsed
						? (japanese ? '詳細パネルを表示' : 'Show details panel')
						: (japanese ? '詳細パネルを隠す' : 'Hide details panel')}
					active={!inspector_collapsed}
					onclick={() => (inspector_collapsed = !inspector_collapsed)}
				>
					<PanelRight size={16} strokeWidth={1.75} />
				</IconButton>
			</div>
			{#if is_loading_scene || is_saving_scene}
				<div class="viewport-scrim">
					<Spinner size={28} />
					<span>
						{is_loading_scene
							? japanese ? 'シーンをロード中…' : 'Loading scene…'
							: japanese ? 'シーンを保存中…' : 'Saving scene…'}
					</span>
				</div>
			{/if}
		{/await}
	</section>

	<!-- =========================================================== inspector -->
	<aside class="inspector" aria-hidden={inspector_collapsed}>
		{#await promise}
			<div class="viewport-status">
				<Spinner size={24} />
			</div>
		{:then}
			<Information bind:this={information_panel} />
		{/await}
	</aside>

	<!-- =============================================================== shelf -->
	<footer class="shelf">
		<div class="shelf-header">
			<button class="shelf-toggle" onclick={() => (shelf_collapsed = !shelf_collapsed)}>
				<span class="chevron" class:rotated={shelf_collapsed}>
					<ChevronDown size={14} strokeWidth={1.75} />
				</span>
				{japanese ? '保存されたシーン' : 'Saved Scenes'}
				<span class="shelf-count">{saved_renderings.length}</span>
			</button>
			{#if !shelf_collapsed}
				<Button
					size="sm"
					variant="secondary"
					disabled={selected_saved_rendering_idx == undefined}
					loading={is_loading_scene}
					onclick={() => loadRendering(selected_saved_rendering_idx)}
				>
					{japanese ? 'シーンを読み込む' : 'Load Scene'}
				</Button>
			{/if}
		</div>
		{#if !shelf_collapsed}
			<div class="shelf-body">
				{#await saved_renderings_promise}
					<div class="shelf-empty"><Spinner size={20} /></div>
				{:then}
					{#if saved_renderings.length === 0}
						<div class="shelf-empty">
							{#if is_loading_saved_renderings}
								<Spinner size={20} />
							{:else}
								{japanese ? '保存されたシーンはまだありません。' : 'No saved scenes yet.'}
							{/if}
						</div>
					{:else}
						{#each saved_renderings as saved, i (i)}
							<Card
								image={imageUrl(saved['rendering_path'])}
								label={(japanese ? 'シーン ' : 'Scene ') + (i + 1)}
								size={72}
								selected={selected_saved_rendering_idx === i}
								onclick={() => (selected_saved_rendering_idx = i)}
								ondblclick={() => loadRendering(i)}
							/>
						{/each}
					{/if}
				{/await}
			</div>
		{/if}
	</footer>
</div>

<!-- ============================================================ design brief -->
<Modal
	bind:open={show_design_brief}
	title={japanese ? 'デザインブリーフ' : 'Design Brief'}
	width="720px"
	onClose={() => (show_design_brief = false)}
>
	<textarea
		class="brief-text"
		placeholder={japanese
			? 'まだデザインブリーフがありません。ここに記入してください。'
			: 'No design brief yet. Write your design brief here, or upload a PDF.'}
		bind:value={design_brief_text}
	></textarea>
	<div class="brief-actions">
		<p class="brief-hint">
			{japanese
				? 'アシスタントの提案とフィードバックは常にこのブリーフを参照します。'
				: 'Every assistant suggestion and feedback is grounded in this brief.'}
		</p>
		<div class="brief-buttons">
			<input
				bind:this={brief_pdf_input}
				type="file"
				accept=".pdf"
				class="hidden-input"
				onchange={uploadBriefPdf}
			/>
			<Button size="sm" variant="secondary" onclick={() => brief_pdf_input?.click()} disabled={is_saving_brief}>
				<Upload size={14} strokeWidth={1.75} />
				{japanese ? 'PDFをアップロード' : 'Upload PDF'}
			</Button>
			<Button size="sm" variant="primary" onclick={saveDesignBrief} loading={is_saving_brief}>
				<Save size={14} strokeWidth={1.75} />
				{japanese ? '保存' : 'Save'}
			</Button>
		</div>
	</div>
</Modal>

<style>
	.shell {
		--tool-col: var(--toolpanel-w);
		--insp-col: var(--inspector-w);
		display: grid;
		grid-template-rows: var(--topbar-h) minmax(0, 1fr) auto;
		grid-template-columns: var(--rail-w) var(--tool-col) minmax(0, 1fr) var(--insp-col);
		grid-template-areas:
			'topbar topbar topbar topbar'
			'rail tool viewport inspector'
			'shelf shelf shelf shelf';
		height: 100vh;
		width: 100vw;
		background: var(--bg-app);
	}

	.shell.tool-collapsed {
		--tool-col: 0px;
	}

	.shell.inspector-collapsed {
		--insp-col: 0px;
	}

	/* ------------------------------------------------------------- top bar */
	.topbar {
		grid-area: topbar;
		display: flex;
		align-items: center;
		gap: var(--sp-3);
		padding: 0 var(--sp-4);
		background: var(--bg-panel);
		border-bottom: 1px solid var(--border-subtle);
	}

	.brand {
		display: flex;
		align-items: center;
		gap: var(--sp-2);
		margin-right: var(--sp-4);
	}

	.brand-mark {
		display: grid;
		place-items: center;
		width: 26px;
		height: 26px;
		border-radius: var(--radius-md);
		background: var(--accent-muted);
		color: var(--accent);
	}

	.brand-name {
		font-size: var(--text-md);
		font-weight: 650;
		letter-spacing: -0.01em;
		white-space: nowrap;
	}

	.topbar-group {
		display: flex;
		align-items: center;
		gap: var(--sp-1);
	}

	.topbar-spacer {
		flex: 1;
	}

	.divider {
		width: 1px;
		height: 20px;
		background: var(--border-subtle);
	}

	.env-picker {
		display: flex;
		align-items: center;
		gap: var(--sp-1);
		color: var(--text-secondary);
	}

	.env-picker select {
		font-family: var(--font-sans);
		font-size: var(--text-sm);
		color: var(--text-primary);
		background: var(--bg-inset);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-md);
		padding: 3px var(--sp-2);
		max-width: 140px;
	}

	.lang-toggle {
		display: flex;
		background: var(--bg-inset);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-md);
		padding: 2px;
		gap: 2px;
	}

	.lang-btn {
		border: none;
		background: transparent;
		color: var(--text-secondary);
		font-size: var(--text-xs);
		font-family: inherit;
		padding: 3px 8px;
		border-radius: var(--radius-sm);
		cursor: pointer;
	}

	.lang-btn.active {
		background: var(--bg-active);
		color: var(--text-primary);
	}

	/* ---------------------------------------------------------------- rail */
	.rail {
		grid-area: rail;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: var(--sp-2);
		padding: var(--sp-3) 0;
		background: var(--bg-panel);
		border-right: 1px solid var(--border-subtle);
	}

	.rail-item {
		position: relative;
	}

	.rail-badge {
		position: absolute;
		top: -3px;
		right: -3px;
		min-width: 15px;
		height: 15px;
		padding: 0 4px;
		display: grid;
		place-items: center;
		font-size: 10px;
		font-weight: 700;
		line-height: 1;
		color: #fff;
		background: var(--danger, #e5484d);
		border-radius: var(--radius-full);
		pointer-events: none;
	}

	/* ---------------------------------------------------------- tool panel */
	.tool-panel {
		grid-area: tool;
		display: flex;
		flex-direction: column;
		min-width: 0;
		overflow: hidden;
		background: var(--bg-panel);
		border-right: 1px solid var(--border-subtle);
	}

	.tool-collapsed .tool-panel {
		display: none;
	}

	.tool-panel-header {
		flex: none;
		padding: var(--sp-3) var(--sp-4);
		font-size: var(--text-sm);
		font-weight: 650;
		border-bottom: 1px solid var(--border-subtle);
	}

	.tool-panel-body {
		flex: 1;
		min-height: 0;
		overflow-y: auto;
	}

	/* ------------------------------------------------------------ viewport */
	.viewport {
		grid-area: viewport;
		position: relative;
		min-width: 0;
		min-height: 0;
		background: var(--bg-inset);
		overflow: hidden;
	}

	.viewport-status {
		height: 100%;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: var(--sp-3);
		color: var(--text-secondary);
		font-size: var(--text-sm);
	}

	.viewport-toolbar {
		position: absolute;
		top: var(--sp-3);
		left: 50%;
		transform: translateX(-50%);
		z-index: 5;
		display: flex;
		gap: var(--sp-1);
		background: var(--bg-elevated);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-lg);
		padding: 3px;
		box-shadow: var(--shadow-overlay);
	}

	.mode-btn {
		display: inline-flex;
		align-items: center;
		gap: 6px;
		border: none;
		background: transparent;
		color: var(--text-secondary);
		font-family: inherit;
		font-size: var(--text-sm);
		padding: 5px 10px;
		border-radius: var(--radius-md);
		cursor: pointer;
		white-space: nowrap;
		transition: background 120ms ease, color 120ms ease;
	}

	.mode-btn:hover {
		background: var(--bg-hover);
		color: var(--text-primary);
	}

	.mode-btn.active {
		background: var(--accent-muted);
		color: var(--accent);
	}

	.viewport-scrim {
		position: absolute;
		inset: 0;
		z-index: 6;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: var(--sp-3);
		background: rgba(10, 12, 15, 0.65);
		color: var(--text-secondary);
		font-size: var(--text-sm);
	}

	/* ----------------------------------------------------------- inspector */
	.inspector {
		grid-area: inspector;
		min-height: 0;
		overflow-y: auto;
		background: var(--bg-panel);
		border-left: 1px solid var(--border-subtle);
	}

	.inspector-collapsed .inspector {
		display: none;
	}

	.inspector-toggle {
		position: absolute;
		top: var(--sp-3);
		right: var(--sp-3);
		z-index: 5;
		background: var(--bg-elevated);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-lg);
		padding: 3px;
		box-shadow: var(--shadow-overlay);
	}

	/* --------------------------------------------------------------- shelf */
	.shelf {
		grid-area: shelf;
		display: flex;
		flex-direction: column;
		height: var(--shelf-h);
		background: var(--bg-panel);
		border-top: 1px solid var(--border-subtle);
	}

	.shelf-collapsed .shelf {
		height: auto;
	}

	.shelf-header {
		flex: none;
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: var(--sp-1) var(--sp-4);
	}

	.shelf-toggle {
		display: inline-flex;
		align-items: center;
		gap: var(--sp-2);
		border: none;
		background: transparent;
		color: var(--text-secondary);
		font-family: inherit;
		font-size: var(--text-sm);
		font-weight: 600;
		padding: var(--sp-1) 0;
		cursor: pointer;
	}

	.shelf-toggle:hover {
		color: var(--text-primary);
	}

	.chevron {
		display: inline-grid;
		place-items: center;
		transition: transform 120ms ease;
	}

	.chevron.rotated {
		transform: rotate(-90deg);
	}

	.shelf-count {
		font-size: var(--text-xs);
		font-weight: 500;
		color: var(--text-muted);
		background: var(--bg-inset);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-full);
		padding: 0 6px;
		line-height: 16px;
	}

	.shelf-body {
		flex: 1;
		min-height: 0;
		display: flex;
		align-items: center;
		gap: var(--sp-2);
		overflow-x: auto;
		padding: 0 var(--sp-4) var(--sp-2);
	}

	.shelf-empty {
		display: flex;
		align-items: center;
		gap: var(--sp-2);
		color: var(--text-muted);
		font-size: var(--text-sm);
	}

	/* --------------------------------------------------------- brief modal */
	.brief-text {
		width: 100%;
		height: 52vh;
		resize: none;
		background: var(--bg-inset);
		color: var(--text-primary);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-md);
		padding: var(--sp-3);
		font-family: inherit;
		font-size: var(--text-base);
		line-height: 1.55;
	}

	.brief-actions {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: var(--sp-3);
		margin-top: var(--sp-3);
	}

	.brief-hint {
		margin: 0;
		font-size: var(--text-xs);
		color: var(--text-muted);
	}

	.brief-buttons {
		display: flex;
		align-items: center;
		gap: var(--sp-2);
	}

	.hidden-input {
		display: none;
	}
</style>

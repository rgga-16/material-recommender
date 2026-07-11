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
	} from './stores.js';

	import { undoAction, redoAction } from './lib/history.js';
	import { showToast } from './lib/toast.js';
	import { imageUrl } from './lib/api.js';

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

	let move_mode = $state(false);
	let tool_panel_collapsed = $state(false);
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
		{ id: 'mat_lib', icon: SwatchBook, en: 'Material Library', ja: '素材ライブラリ' },
		{ id: 'upload', icon: Upload, en: 'Upload', ja: 'アップロード' },
		{ id: 'auto_style', icon: WandSparkles, en: 'Auto-Style', ja: '自動スタイル' },
	];

	function railClick(id) {
		if ($actions_panel_tab === id && !tool_panel_collapsed) {
			tool_panel_collapsed = true;
		} else {
			tool_panel_collapsed = false;
			actions_panel_tab.set(id);
		}
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
		loadHdris();
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

<div class="shell" class:tool-collapsed={tool_panel_collapsed} class:shelf-collapsed={shelf_collapsed}>
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
				<IconButton
					label={japanese ? item.ja : item.en}
					active={$actions_panel_tab === item.id && !tool_panel_collapsed}
					onclick={() => railClick(item.id)}
				>
					<item.icon size={20} strokeWidth={1.75} />
				</IconButton>
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
	<aside class="inspector">
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
		placeholder="No design brief yet. Please write your design brief here."
		readonly={true}
		bind:value={design_brief_text}
	></textarea>
</Modal>

<style>
	.shell {
		display: grid;
		grid-template-rows: var(--topbar-h) minmax(0, 1fr) auto;
		grid-template-columns: var(--rail-w) var(--toolpanel-w) minmax(0, 1fr) var(--inspector-w);
		grid-template-areas:
			'topbar topbar topbar topbar'
			'rail tool viewport inspector'
			'shelf shelf shelf shelf';
		height: 100vh;
		width: 100vw;
		background: var(--bg-app);
	}

	.shell.tool-collapsed {
		grid-template-columns: var(--rail-w) 0 minmax(0, 1fr) var(--inspector-w);
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
</style>

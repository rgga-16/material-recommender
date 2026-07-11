<script>
    // Proactive design-feedback feed. Entries arrive asynchronously from the
    // feedback scheduler (lib/feedbackScheduler.js); every critique is
    // grounded in the design brief and, when a vision model is pulled, the
    // scene's rendered appearance. Newest first.
    import SvelteMarkdown from '@humanspeak/svelte-markdown';

    import DynamicImage from '../DynamicImage.svelte';
    import Button from '../../lib/ui/Button.svelte';
    import PanelSection from '../../lib/ui/PanelSection.svelte';
    import Spinner from '../../lib/ui/Spinner.svelte';

    import WandSparkles from '@lucide/svelte/icons/wand-sparkles';
    import RefreshCw from '@lucide/svelte/icons/refresh-cw';

    import { feedback_feed, in_japanese, generate_tab_page, actions_panel_tab } from '../../stores.js';
    import { generator, viewport } from '../../lib/registry.js';
    import { postJson } from '../../lib/api.js';
    import { pollJob } from '../../lib/jobs.js';
    import { showToast } from '../../lib/toast.js';

    let japanese = $derived($in_japanese);
    let feed = $derived($feedback_feed);

    let is_requesting = $state(false);
    let progress_message = $state('');

    /** Manual "review now" — same pipeline as the scheduler, on demand. */
    async function requestFeedbackNow() {
        is_requesting = true;
        progress_message = '';
        let screenshot = null;
        try {
            screenshot = viewport.get()?.captureScreenshot(1) ?? null;
        } catch (error) {
            console.warn('scene screenshot unavailable', error);
        }
        try {
            const submit = await postJson('/feedback_scene', { screenshot });
            const data = await pollJob(submit.job_id, {
                onProgress: (job) => { progress_message = job.message || ''; },
            });
            feedback_feed.update((f) => [{
                id: `${Date.now()}`,
                at: new Date(),
                summary: data['summary'] || '',
                observations: data['observations'] || [],
                references: data['references'] || '',
            }, ...f]);
        } catch (error) {
            console.error(error);
            showToast(error.message, 'error');
        } finally {
            is_requesting = false;
            progress_message = '';
        }
    }

    function generate(name) {
        actions_panel_tab.set('generate');
        generate_tab_page.set(0);
        generator.get()?.generate_textures(name);
    }

    function timestamp(at) {
        try {
            return new Date(at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        } catch {
            return '';
        }
    }
</script>

<div class="feedback-panel">
    <div class="panel-head">
        <p class="panel-hint">
            {japanese
                ? 'シーンの変更後、デザインブリーフに基づいたフィードバックが自動的にここに届きます。'
                : 'Feedback on your scene arrives here automatically as you work, always judged against the design brief.'}
        </p>
        <Button size="sm" variant="secondary" onclick={requestFeedbackNow} loading={is_requesting}>
            <RefreshCw size={14} strokeWidth={1.75} />
            {japanese ? '今すぐレビュー' : 'Review now'}
        </Button>
        {#if is_requesting && progress_message}
            <div class="progress-line"><Spinner size={14} /> {progress_message}</div>
        {/if}
    </div>

    {#if feed.length === 0}
        <div class="empty-state">
            {japanese
                ? 'まだフィードバックはありません。テクスチャを適用すると、アシスタントがシーンをレビューします。'
                : 'No feedback yet. Apply some textures and the assistant will review your scene.'}
        </div>
    {:else}
        <div class="feed">
            {#each feed as entry, i (entry.id)}
                <PanelSection title={(japanese ? 'フィードバック ' : 'Feedback ') + timestamp(entry.at)} open={i === 0}>
                    {#if entry.summary}
                        <p class="summary">{entry.summary}</p>
                    {/if}
                    {#each entry.observations as obs, oi (oi)}
                        <div class="observation">
                            {#if obs.aspect}
                                <div class="aspect">{obs.aspect}</div>
                            {/if}
                            <p class="obs-text">{obs.text}</p>
                            {#if obs.suggestions?.length > 0}
                                <div class="suggestion-grid">
                                    {#each obs.suggestions as s, si (si)}
                                        <div class="suggestion-card">
                                            <span class="suggestion-name">{s.name}</span>
                                            {#if s.filepath}
                                                <DynamicImage imagepath={s.filepath} alt={s.name} size="96px" is_draggable={s.kind === 'material'} />
                                            {/if}
                                            <span class="suggestion-kind">{s.kind}</span>
                                            {#if s.kind === 'material'}
                                                <Button size="sm" variant="secondary" onclick={() => generate(s.name)}>
                                                    <WandSparkles size={14} strokeWidth={1.75} />
                                                    {japanese ? 'もっと生成' : 'Generate more'}
                                                </Button>
                                            {/if}
                                        </div>
                                    {/each}
                                </div>
                            {/if}
                        </div>
                    {/each}
                    {#if entry.references}
                        <div class="references"><SvelteMarkdown source={entry.references} /></div>
                    {/if}
                </PanelSection>
            {/each}
        </div>
    {/if}
</div>

<style>
    .feedback-panel {
        display: flex;
        flex-direction: column;
        gap: var(--sp-3);
        width: 100%;
        height: 100%;
        min-height: 0;
    }

    .panel-head {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        gap: var(--sp-2);
    }

    .panel-hint {
        margin: 0;
        font-size: var(--text-xs);
        color: var(--text-muted);
        line-height: 1.5;
    }

    .progress-line {
        display: flex;
        align-items: center;
        gap: var(--sp-2);
        font-size: var(--text-xs);
        color: var(--text-secondary);
    }

    .empty-state {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        color: var(--text-muted);
        font-size: var(--text-sm);
        padding: var(--sp-4);
        line-height: 1.6;
    }

    .feed {
        flex: 1;
        min-height: 0;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: var(--sp-2);
    }

    .summary {
        margin: 0;
        font-size: var(--text-sm);
        line-height: 1.6;
        font-weight: 550;
    }

    .observation {
        display: flex;
        flex-direction: column;
        gap: var(--sp-1);
        padding: var(--sp-2);
        background: var(--bg-inset);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        margin-bottom: var(--sp-2);
    }

    .aspect {
        font-size: var(--text-xs);
        font-weight: 600;
        color: var(--accent);
        text-transform: capitalize;
    }

    .obs-text {
        margin: 0;
        font-size: var(--text-sm);
        line-height: 1.55;
    }

    .suggestion-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
        gap: var(--sp-2);
        margin-top: var(--sp-1);
    }

    .suggestion-card {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: var(--sp-1);
        background: var(--bg-elevated);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        padding: var(--sp-2);
        text-align: center;
    }

    .suggestion-name {
        font-size: var(--text-sm);
        font-weight: 600;
    }

    .suggestion-kind {
        font-size: var(--text-xs);
        color: var(--text-muted);
        text-transform: capitalize;
    }

    .references {
        font-size: var(--text-xs);
        color: var(--text-secondary);
    }
</style>

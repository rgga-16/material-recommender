<script>
    import { onMount } from 'svelte';
    import { get } from 'svelte/store';
    import SvelteMarkdown from '@humanspeak/svelte-markdown';

    import MaterialCard from '../SuggestModule/MaterialCard.svelte';
    import ColorPalette from '../SuggestModule/ColorPalette.svelte';

    import Spinner from '../../lib/ui/Spinner.svelte';
    import TextInput from '../../lib/ui/TextInput.svelte';
    import IconButton from '../../lib/ui/IconButton.svelte';
    import Button from '../../lib/ui/Button.svelte';
    import Switch from '../../lib/ui/Switch.svelte';

    import Send from '@lucide/svelte/icons/send';
    import MessageCircle from '@lucide/svelte/icons/message-circle';
    import Palette from '@lucide/svelte/icons/palette';
    import Bookmark from '@lucide/svelte/icons/bookmark';
    import WandSparkles from '@lucide/svelte/icons/wand-sparkles';
    import RefreshCw from '@lucide/svelte/icons/refresh-cw';
    import ChevronDown from '@lucide/svelte/icons/chevron-down';
    import ChevronUp from '@lucide/svelte/icons/chevron-up';

    import { saved_color_palettes } from '../../stores.js';
    import { chatbot_input_message } from '../../stores.js';
    import { design_brief } from '../../stores.js';
    import { actions_panel_tab } from '../../stores.js';
    import { generate_tab_page } from '../../stores.js';
    import { in_japanese } from '../../stores.js';

    import { translate } from '../../lib/i18n.js';
    import { showToast } from '../../lib/toast.js';
    import { sessionId, streamChat } from '../../lib/api.js';
    import { pollJob } from '../../lib/jobs.js';

    let { onProceedToGenerate = () => {} } = $props();

    let japanese = $derived($in_japanese);

    let inputMessage = $state('');
    let use_internet = $state(false);

    let messages = $state([]);
    /*
    Let the message dictionary format be:
    {
        "message": "Hello",
        "role": "user",
        "type": "regular" OR "suggested_materials" OR "suggested_color palettes"
        "content": [list of suggested materials or color palettes] if type is "suggested_materials" or "suggested_color palettes"
    }
    */

    let suggested_material_queries = $state([
        "What are some wood materials that are generally low-cost?",
        "What materials would you suggest that are eco-friendly and sustainable?",
        "What materials do you recommend for a modern-style interior bedroom?",
        "Can you suggest materials that are durable in a high-traffic commercial space?",
        "Can you suggest materials that can be locally sourced in [location]?"
    ]);

    let expanded_suggested_questions = $state(false);
    function expand() {
        expanded_suggested_questions = !expanded_suggested_questions;
    }

    let use_design_brief = $state(false);

    let is_loading_response = $state(false);
    let is_loading_material_queries = $state(false);
    let loading_message = $state('');

    // Shared fetch helper: surfaces the backend's LLM-unavailable response
    // (503 with a JSON {error} body) as a toast, and rethrows so callers can
    // stop their own loading state in a finally block.
    async function fetchJson(url, options) {
        const response = await fetch(url, options);
        if (!response.ok) {
            const err_json = await response.json().catch(() => ({}));
            const message = err_json.error
                || (japanese ? `リクエストに失敗しました（${response.status}）。` : `Request failed (${response.status}).`);
            showToast(message, 'error');
            throw new Error(message);
        }
        return response.json();
    }

    async function suggest_materials() {
        if (inputMessage.trim() === '') {
            showToast(japanese ? "クエリを入力してください。" : "Please enter a query.", 'error');
            return;
        }
        messages.push({
            "message": inputMessage,
            "role": "user",
            "type": "regular"
        });
        messages = messages;
        is_loading_response = true;

        let context = null;
        if (use_design_brief) {
            context = get(design_brief);
        }

        try {
            const submit = await fetchJson("/suggest_materials", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    "prompt": japanese ? await translate("JA", "EN-US", inputMessage) : inputMessage,
                    "role": "user",
                    "use_internet": use_internet,
                    "context": context,
                    "session_id": sessionId()
                }),
            });

            // Suggestions run as a background job (LLM + one texture per
            // material); follow it over SSE and surface its progress.
            const json = await pollJob(submit.job_id, {
                onProgress: (job) => { loading_message = job.message || ''; }
            });

            inputMessage = '';

            let intro_text = json["intro_text"];
            let role = json["role"];
            let suggested_materials = json["suggested_materials"];
            console.log(suggested_materials);

            let message_type = "suggested_materials";
            messages.push({
                "message": intro_text,
                "role": role,
                "type": message_type,
                "content": suggested_materials
            });
            messages = messages;
        } catch (error) {
            console.error(error);
            showToast(error.message, 'error');
        } finally {
            is_loading_response = false;
            loading_message = '';
        }
    }

    async function suggest_color_palettes() {
        if (inputMessage.trim() === '') {
            showToast(japanese ? "クエリを入力してください。" : "Please enter a query.", 'error');
            return;
        }

        messages.push({
            "message": inputMessage,
            "role": "user",
            "type": "regular"
        });
        messages = messages;
        is_loading_response = true;

        try {
            const json = await fetchJson("/suggest_colors", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    "prompt": inputMessage,
                    "role": "user",
                    "use_internet": use_internet
                }),
            });

            inputMessage = '';

            let intro_text = json["intro_text"];
            let role = json["role"];
            let suggested_color_palettes = json["suggested_color_palettes"];

            if (japanese) {
                for (let i = 0; i < suggested_color_palettes.length; i++) {
                    suggested_color_palettes[i]["name"] = await translate("EN", "JA", suggested_color_palettes[i]["name"]);
                    suggested_color_palettes[i]["description"] = await translate("EN", "JA", suggested_color_palettes[i]["description"]);
                }
            }

            let message_type = "suggested_color_palettes";
            messages.push({
                "message": intro_text,
                "role": role,
                "type": message_type,
                "content": suggested_color_palettes
            });
            messages = messages;
        } catch (error) {
            console.error(error);
        } finally {
            is_loading_response = false;
        }
    }

    function saveColorPalette(color_palette) {
        let dict = {
            name: color_palette["name"],
            palette: color_palette["codes"]
        }
        saved_color_palettes.update(lst => lst.concat(dict));
        showToast(japanese ? "カラーパレットが保存されました！" : "Color palette saved!", 'success');
    }

    async function query() {
        if (inputMessage.trim() === '') {
            return;
        }

        messages.push({
            "message": inputMessage,
            "role": "user"
        });
        // Placeholder assistant bubble that fills in as tokens stream.
        const reply = { "message": "", "role": "assistant" };
        messages.push(reply);
        messages = messages;

        const prompt = inputMessage;
        inputMessage = '';

        try {
            await streamChat("/query_stream", {
                "prompt": prompt,
                "role": "user",
                "session_id": sessionId(),
            }, {
                onDelta: (_chunk, full) => {
                    reply.message = full;
                    messages = messages;
                }
            });
        } catch (error) {
            console.error(error);
            showToast(error.message, 'error');
            reply.message = reply.message ||
                (japanese ? "応答を取得できませんでした。" : "Could not get a response.");
            messages = messages;
        }
    }

    async function init_query() {
        is_loading_response = true;
        try {
            const json = await fetchJson(`./init_query?session_id=${encodeURIComponent(sessionId())}`);

            let message = json["response"];
            let role = json["role"];

            if (japanese) {
                message = await translate("EN", "JA", message);
            }

            messages.push({
                "message": message,
                "role": role
            });
            messages = messages;
        } catch (error) {
            console.error(error);
        } finally {
            is_loading_response = false;
        }
    }

    async function brainstorm_material_queries() {
        suggested_material_queries = [];
        is_loading_material_queries = true;
        try {
            const json = await fetchJson('./brainstorm_material_queries');
            suggested_material_queries = json['prompts'];
        } catch (error) {
            console.error(error);
        } finally {
            is_loading_material_queries = false;
        }
    }

    function generate(material_name) {
        actions_panel_tab.set("generate");
        generate_tab_page.set(0);
        onProceedToGenerate(material_name);
    }

    $effect(() => {
        // If the chatbot_input_message global store is updated (e.g. by
        // another module composing a query for the chatbot), mirror it into
        // the composer's input.
        inputMessage = $chatbot_input_message;
    });

    onMount(async () => {
        await init_query(); // COMMENT IF YOU DON'T WANT TO USE THE CHATBOT
    });

</script>

<div class="chatbot">
    <div class="messages">
        {#each messages as message}
            <div class="message-row {message.role}">
                <div class="bubble {message.role}">
                    <div class="bubble-role">
                        {#if japanese}
                            {#if message.role == "user"}
                                あなた
                            {:else if message.role == "assistant"}
                                アシスタント
                            {/if}
                        {:else}
                            {message.role}
                        {/if}
                    </div>
                    <div class="markdown-content">
                        <SvelteMarkdown source={message.message} />
                    </div>
                    {#if message.type == "suggested_materials"}
                        <div class="material-suggestions">
                            {#each message.content as m, i}
                                <MaterialCard material_path={m["filepath"]} material_name={m["name"]} material_info={m["reason"]} index={i} />
                                <Button variant="ghost" size="sm" onclick={() => generate(m["name"])}>
                                    <WandSparkles size={14} strokeWidth={1.75} />
                                    {japanese ? "もっと生み出せ！" : "Generate more!"}
                                </Button>
                            {/each}
                        </div>
                    {:else if message.type == "suggested_color_palettes"}
                        <div class="color-suggestions">
                            {#each message.content as m}
                                <div class="color-suggestion-card">
                                    <ColorPalette name={m["name"]} color_codes={m["codes"]} />
                                    <Button variant="ghost" size="sm" onclick={() => saveColorPalette(m)}>
                                        <Bookmark size={14} strokeWidth={1.75} />
                                        {japanese ? "パレットを保存する" : "Save Palette"}
                                    </Button>
                                    <div class="markdown-content">
                                        <SvelteMarkdown source={m["description"]} />
                                    </div>
                                </div>
                            {/each}
                        </div>
                    {/if}
                </div>
            </div>
        {/each}

        {#if is_loading_response}
            <div class="message-row assistant">
                <div class="bubble assistant loading">
                    <Spinner size={18} />
                    <span>
                        {loading_message
                            ? loading_message
                            : (japanese ? "応答を読み込んでいます。しばらくお待ちください。" : "Loading response, please wait. This may take a while.")}
                    </span>
                </div>
            </div>
        {/if}
    </div>

    <div class="composer">
        <div class="starter-chips">
            <div class="chips-row">
                {#each (expanded_suggested_questions ? suggested_material_queries : suggested_material_queries.slice(0, 2)) as q}
                    <button type="button" class="chip" onclick={() => (inputMessage = q)}>{q}</button>
                {/each}
            </div>
            <div class="chips-actions">
                {#if suggested_material_queries.length > 2}
                    <IconButton
                        size="sm"
                        label={expanded_suggested_questions ? (japanese ? "折りたたむ" : "Show fewer") : (japanese ? "もっと見る" : "Show more")}
                        onclick={expand}
                    >
                        {#if expanded_suggested_questions}
                            <ChevronUp size={14} strokeWidth={1.75} />
                        {:else}
                            <ChevronDown size={14} strokeWidth={1.75} />
                        {/if}
                    </IconButton>
                {/if}
                <IconButton
                    size="sm"
                    label={japanese ? "新しい質問案を生成する" : "Brainstorm new prompts"}
                    onclick={brainstorm_material_queries}
                    disabled={is_loading_material_queries}
                >
                    {#if is_loading_material_queries}
                        <Spinner size={14} />
                    {:else}
                        <RefreshCw size={14} strokeWidth={1.75} />
                    {/if}
                </IconButton>
            </div>
        </div>

        <div class="composer-input-row">
            <TextInput
                bind:value={inputMessage}
                placeholder={japanese ? "ここに資料やカラーパレットに関するお問い合わせを入力してください。" : "Type your queries for materials or color palettes here..."}
                onEnter={() => suggest_materials()}
            />
            <IconButton label={japanese ? "送信" : "Send"} onclick={() => suggest_materials()}>
                <Send size={16} strokeWidth={1.75} />
            </IconButton>
        </div>

        <div class="composer-toolbar">
            <div class="toggles">
                <Switch bind:checked={use_internet} label={japanese ? "ウェブ検索" : "Web search"} />
                <Switch bind:checked={use_design_brief} label={japanese ? "デザイン・ブリーフ" : "Design brief"} />
            </div>
            <div class="toolbar-actions">
                <Button variant="ghost" size="sm" onclick={() => query()}>
                    <MessageCircle size={14} strokeWidth={1.75} />
                    {japanese ? "チャット" : "Chat"}
                </Button>
                <Button variant="ghost" size="sm" onclick={() => suggest_color_palettes()}>
                    <Palette size={14} strokeWidth={1.75} />
                    {japanese ? "色を提案する" : "Suggest Colors"}
                </Button>
            </div>
        </div>
    </div>
</div>

<style>
    .chatbot {
        display: flex;
        flex-direction: column;
        height: 100%;
        min-height: 0;
        width: 100%;
        gap: var(--sp-2);
    }

    .messages {
        flex: 1 1 auto;
        min-height: 0;
        display: flex;
        flex-direction: column;
        gap: var(--sp-3);
        overflow-y: auto;
        padding: var(--sp-2) var(--sp-1);
    }

    .message-row {
        display: flex;
        width: 100%;
    }

    .message-row.user {
        justify-content: flex-end;
    }

    .message-row.assistant {
        justify-content: flex-start;
    }

    .bubble {
        max-width: 88%;
        display: flex;
        flex-direction: column;
        gap: var(--sp-1);
        padding: var(--sp-2) var(--sp-3);
        border-radius: var(--radius-lg);
        font-size: var(--text-base);
        line-height: 1.55;
        color: var(--text-primary);
    }

    .bubble.user {
        background: var(--accent-muted);
    }

    .bubble.assistant {
        background: var(--bg-elevated);
    }

    .bubble.loading {
        flex-direction: row;
        align-items: center;
        gap: var(--sp-2);
        color: var(--text-muted);
    }

    .bubble-role {
        font-size: var(--text-xs);
        font-weight: 600;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.02em;
    }

    .markdown-content :global(p) {
        margin: 0 0 var(--sp-2) 0;
    }

    .markdown-content :global(p:last-child) {
        margin-bottom: 0;
    }

    .markdown-content :global(ul),
    .markdown-content :global(ol) {
        margin: 0 0 var(--sp-2) 0;
        padding-left: var(--sp-4);
    }

    .markdown-content :global(li) {
        margin-bottom: var(--sp-1);
    }

    .markdown-content :global(code) {
        background: var(--bg-inset);
        padding: 1px 4px;
        border-radius: var(--radius-sm);
        font-size: var(--text-sm);
    }

    .markdown-content :global(pre) {
        background: var(--bg-inset);
        padding: var(--sp-2);
        border-radius: var(--radius-md);
        overflow-x: auto;
    }

    .markdown-content :global(pre code) {
        background: none;
        padding: 0;
    }

    .markdown-content :global(a) {
        color: var(--accent);
    }

    .markdown-content :global(strong) {
        font-weight: 600;
    }

    .material-suggestions,
    .color-suggestions {
        display: flex;
        flex-direction: column;
        gap: var(--sp-2);
    }

    .color-suggestion-card {
        display: flex;
        flex-direction: column;
        gap: var(--sp-1);
        padding: var(--sp-2);
        background: var(--bg-inset);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
    }

    .composer {
        flex: 0 0 auto;
        display: flex;
        flex-direction: column;
        gap: var(--sp-2);
        padding-top: var(--sp-2);
        border-top: 1px solid var(--border-subtle);
    }

    .starter-chips {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: var(--sp-2);
    }

    .chips-row {
        display: flex;
        flex-wrap: wrap;
        gap: var(--sp-1);
    }

    .chips-actions {
        display: flex;
        align-items: center;
        gap: var(--sp-1);
        flex-shrink: 0;
    }

    .chip {
        font-family: var(--font-sans);
        font-size: var(--text-xs);
        color: var(--text-secondary);
        background: transparent;
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-full);
        padding: var(--sp-1) var(--sp-2);
        cursor: pointer;
        transition:
            background 120ms ease,
            border-color 120ms ease,
            color 120ms ease;
    }

    .chip:hover {
        background: var(--bg-hover);
        border-color: var(--border-strong);
        color: var(--text-primary);
    }

    .composer-input-row {
        display: flex;
        align-items: center;
        gap: var(--sp-2);
    }

    .composer-toolbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: var(--sp-2);
    }

    .toggles {
        display: flex;
        align-items: center;
        gap: var(--sp-4);
    }

    .toolbar-actions {
        display: flex;
        align-items: center;
        gap: var(--sp-1);
    }
</style>

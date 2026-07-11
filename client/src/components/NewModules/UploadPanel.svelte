<script>
    // Upload your own rooms and furniture (.glb, .gltf, .obj, .fbx, .stl).
    // The file is parsed client-side: every mesh node becomes a selectable,
    // texturable part in the scene manifest (schema v2: parts share one model
    // file and reference their mesh via "node"). No manual pre-cutting or
    // manifest authoring needed — parts are auto-detected.
    import { parseModelFile } from '../../lib/three/loaders.js';
    import { get } from 'svelte/store';

    import { curr_texture_parts } from '../../stores.js';
    import { object_transforms } from '../../stores.js';
    import { viewport } from '../../lib/registry.js';
    import { in_japanese } from '../../stores.js';
    import { showToast } from '../../lib/toast.js';

    import Upload from '@lucide/svelte/icons/upload';
    import Trash2 from '@lucide/svelte/icons/trash-2';
    import Button from '../../lib/ui/Button.svelte';
    import IconButton from '../../lib/ui/IconButton.svelte';
    import TextInput from '../../lib/ui/TextInput.svelte';
    import Field from '../../lib/ui/Field.svelte';
    import Spinner from '../../lib/ui/Spinner.svelte';

    let japanese = $derived($in_japanese);
    let scene_objects = $derived(Object.keys($curr_texture_parts || {}));

    let file_input = $state(null);
    let drag_over = $state(false);
    let is_uploading = $state(false);
    let selected_file = $state(null);
    let object_name = $state("");

    const MODEL_EXT_RE = /\.(glb|gltf|obj|fbx|stl)$/i;

    function chooseFile(files) {
        if (!files || files.length === 0) return;
        const file = files[0];
        if (!MODEL_EXT_RE.test(file.name)) {
            showToast(japanese
                ? ".glb / .gltf / .obj / .fbx / .stl ファイルをアップロードしてください。"
                : "Please upload a .glb, .gltf, .obj, .fbx, or .stl file.", 'error');
            return;
        }
        selected_file = file;
        if (!object_name) {
            object_name = file.name.replace(MODEL_EXT_RE, '');
        }
    }

    function onDrop(event) {
        event.preventDefault();
        drag_over = false;
        chooseFile(event.dataTransfer.files);
    }

    async function parseMeshNodes(file) {
        // parseModelFile normalizes names/UVs exactly like the scene loader
        // will, so the node names recorded here resolve after upload.
        const root = await parseModelFile(file);
        const nodes = [];
        root.traverse((child) => {
            if (child.isMesh) nodes.push(child.name || "part");
        });
        return nodes;
    }

    async function upload() {
        if (!selected_file || is_uploading) return;
        is_uploading = true;
        try {
            const mesh_nodes = await parseMeshNodes(selected_file);
            if (mesh_nodes.length === 0) {
                throw new Error(japanese ? "ファイルにメッシュが見つかりませんでした。" : "No meshes found in the file.");
            }

            const form_data = new FormData();
            form_data.append('file', selected_file);
            form_data.append('object_name', object_name || 'object');
            const upload_response = await fetch('/upload_model', { method: 'POST', body: form_data });
            const upload_data = await upload_response.json();
            if (!upload_response.ok) {
                throw new Error(upload_data.error || "Upload failed.");
            }

            // Build one manifest entry per uniquely-named mesh node.
            const texture_parts = get(curr_texture_parts) || {};
            let obj_name = upload_data.object_name;
            let base_name = obj_name;
            let suffix = 2;
            while (texture_parts[obj_name]) {
                obj_name = base_name + suffix;
                suffix += 1;
            }

            const parts = {};
            let skipped_duplicates = 0;
            for (const node_name of mesh_nodes) {
                if (parts[node_name]) {
                    skipped_duplicates += 1;
                    continue;
                }
                parts[node_name] = {
                    "is_selectable": true,
                    "mat_name": "none",
                    "mat_image_texture": null,
                    "mat_normal_texture": null,
                    "mat_height_texture": null,
                    "color": "#FFFFFF",
                    "opacity": 1.0,
                    "roughness": 0.5,
                    "metalness": 0.0,
                    "offsetX": 0.0,
                    "offsetY": 0.0,
                    "rotation": 0.0,
                    "scaleX": 1.0,
                    "scaleY": 1.0,
                    "model": upload_data.model_path,
                    "node": node_name,
                    "parents": []
                };
            }
            texture_parts[obj_name] = parts;

            const manifest_response = await fetch('/update_manifest', {
                method: 'POST',
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ "texture_parts": texture_parts }),
            });
            const manifest_data = await manifest_response.json();
            curr_texture_parts.set(manifest_data.texture_parts);

            viewport.get()?.update_3d_scene();

            const part_count = Object.keys(parts).length;
            let message = japanese
                ? `「${obj_name}」を追加しました(${part_count}個のパーツ)。`
                : `Added "${obj_name}" with ${part_count} part${part_count === 1 ? '' : 's'}.`;
            if (skipped_duplicates > 0) {
                message += japanese
                    ? ` 同名メッシュ${skipped_duplicates}個は個別選択できません。`
                    : ` ${skipped_duplicates} duplicate-named mesh(es) won't be individually selectable.`;
            }
            showToast(message, 'success');

            selected_file = null;
            object_name = "";
            if (file_input) file_input.value = "";
        } catch (error) {
            console.error(error);
            showToast((japanese ? "アップロードに失敗しました: " : "Upload failed: ") + error.message, 'error');
        }
        is_uploading = false;
    }

    async function removeObject(obj_name) {
        try {
            const response = await fetch('/remove_object', {
                method: 'POST',
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ "object": obj_name }),
            });
            const data = await response.json();
            curr_texture_parts.set(data.texture_parts);
            object_transforms.set(data.transforms || {});
            viewport.get()?.update_3d_scene();
            showToast(japanese ? `「${obj_name}」を削除しました。` : `Removed "${obj_name}".`, 'success');
        } catch (error) {
            console.error(error);
            showToast(japanese ? "削除に失敗しました。" : "Failed to remove object.", 'error');
        }
    }
</script>

<div class="upload-panel">
    <div class="section">
        <h3 class="section-title">{japanese ? "モデルをアップロード" : "Upload Model"}</h3>
        <p class="hint">
            {japanese
                ? "部屋や家具の3Dファイル(.glb/.gltf/.obj/.fbx/.stl)をアップロードします。各メッシュが自動的に選択・テクスチャ適用可能なパーツになります。.mtl等の外部マテリアルは無視されます。"
                : "Upload a room or furniture model (.glb, .gltf, .obj, .fbx, .stl). Every mesh is auto-detected as a selectable, texturable part — no manual cutting needed. External materials (e.g. .mtl) are ignored."}
        </p>

        <div
            class="dropzone"
            class:drag-over={drag_over}
            ondragover={(e) => { e.preventDefault(); drag_over = true; }}
            ondragleave={() => (drag_over = false)}
            ondrop={onDrop}
            onclick={() => file_input?.click()}
            onkeydown={(e) => { if (e.key === 'Enter') file_input?.click(); }}
            role="button"
            tabindex="0"
        >
            <Upload size={24} strokeWidth={1.75} />
            {#if selected_file}
                <span class="dropzone-text">
                    <strong>{selected_file.name}</strong>
                    <span class="hint">({Math.round(selected_file.size / 1024)} KB)</span>
                </span>
            {:else}
                <span class="dropzone-text">
                    {japanese
                        ? "ここに3Dモデルをドロップ、またはクリックして選択"
                        : "Drop a 3D model here or click to browse"}
                </span>
            {/if}
        </div>
        <input
            type="file"
            accept=".glb,.gltf,.obj,.fbx,.stl"
            bind:this={file_input}
            class="hidden-input"
            onchange={(e) => chooseFile(e.target.files)}
        />

        <Field label={japanese ? "オブジェクト名" : "Object name"}>
            <TextInput bind:value={object_name} placeholder={japanese ? "例: ソファ" : "e.g. sofa"} />
        </Field>

        <Button variant="primary" fullWidth disabled={!selected_file || is_uploading} onclick={upload}>
            {japanese ? "シーンに追加" : "Add to Scene"}
        </Button>

        {#if is_uploading}
            <div class="upload-status">
                <Spinner size={16} />
                <span>{japanese ? "アップロード中..." : "Uploading..."}</span>
            </div>
        {/if}
    </div>

    <div class="section">
        <h3 class="section-title">{japanese ? "シーン内のオブジェクト" : "Objects in Scene"}</h3>
        <p class="hint">
            {japanese
                ? "「オブジェクトを移動」モードで配置を調整できます(g/r/sキーで移動・回転・拡縮)。"
                : "Use \"Move Objects\" mode under the 3D view to reposition them (g/r/s keys: move/rotate/scale)."}
        </p>
        <ul class="object-list">
            {#each scene_objects as obj (obj)}
                <li class="object-row">
                    <span class="object-name">{obj}</span>
                    <span class="remove-wrap">
                        <IconButton label={japanese ? "削除" : "Remove"} onclick={() => removeObject(obj)}>
                            <Trash2 size={16} strokeWidth={1.75} />
                        </IconButton>
                    </span>
                </li>
            {:else}
                <li class="empty-state">
                    {japanese ? "シーンにオブジェクトがありません。" : "No objects in the scene yet."}
                </li>
            {/each}
        </ul>
    </div>
</div>

<style>
    .upload-panel {
        display: flex;
        flex-direction: column;
        gap: var(--sp-5);
        overflow-y: auto;
    }

    .section {
        display: flex;
        flex-direction: column;
        gap: var(--sp-2);
    }

    .section-title {
        margin: 0;
        font-size: var(--text-sm);
        font-weight: 600;
        color: var(--text-primary);
    }

    .hint {
        margin: 0;
        font-size: var(--text-xs);
        color: var(--text-secondary);
    }

    .dropzone {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: var(--sp-2);
        padding: var(--sp-5) var(--sp-3);
        border: 2px dashed var(--border-strong);
        border-radius: var(--radius-lg);
        color: var(--text-secondary);
        text-align: center;
        cursor: pointer;
        transition:
            border-color 120ms ease,
            background 120ms ease,
            color 120ms ease;
    }

    .dropzone:hover {
        border-color: var(--accent);
    }

    .dropzone.drag-over {
        border-color: var(--accent);
        background: var(--accent-muted);
        color: var(--text-primary);
    }

    .dropzone-text {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: var(--sp-1);
        font-size: var(--text-base);
    }

    .dropzone-text strong {
        color: var(--text-primary);
        font-weight: 600;
    }

    .hidden-input {
        display: none;
    }

    .upload-status {
        display: flex;
        align-items: center;
        gap: var(--sp-2);
        font-size: var(--text-sm);
        color: var(--text-secondary);
    }

    .object-list {
        list-style: none;
        margin: 0;
        padding: 0;
        display: flex;
        flex-direction: column;
        gap: var(--sp-1);
        overflow-y: auto;
    }

    .object-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: var(--sp-2);
        padding: var(--sp-2) var(--sp-1);
        border-bottom: 1px solid var(--border-subtle);
    }

    .object-name {
        font-size: var(--text-base);
        color: var(--text-primary);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .remove-wrap :global(button):hover {
        color: var(--danger);
    }

    .empty-state {
        padding: var(--sp-3) 0;
        text-align: center;
        font-size: var(--text-sm);
        color: var(--text-muted);
    }
</style>

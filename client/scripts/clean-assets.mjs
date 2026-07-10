// Pre-build cleanup scoped to Vite's own outputs. public/ doubles as Flask's
// static root with runtime-generated content (gen_images/, preset_materials/),
// so we must never delete anything beyond what the previous build emitted.
import { rm } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

const out = (p) => fileURLToPath(new URL(`../public/${p}`, import.meta.url));

await rm(out('assets'), { recursive: true, force: true });
await rm(out('index.html'), { force: true });

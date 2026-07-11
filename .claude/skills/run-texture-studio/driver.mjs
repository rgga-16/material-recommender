// Headless driver for Texture Studio (Flask on :2099 + Svelte/Three.js UI).
//
// Uses playwright-core with the system Edge/Chrome (no browser download).
// The Flask server must already be running — see SKILL.md.
//
//   node .claude/skills/run-texture-studio/driver.mjs smoke
//   node .claude/skills/run-texture-studio/driver.mjs generate "brushed copper"
//
// Screenshots land in .claude/skills/run-texture-studio/screenshots/.
// Exits non-zero on page errors, console errors, or missing UI.
import { createRequire } from 'node:module';
import { mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const skillDir = dirname(fileURLToPath(import.meta.url));
const repoRoot = join(skillDir, '..', '..', '..');
const shotsDir = join(skillDir, 'screenshots');
mkdirSync(shotsDir, { recursive: true });

// playwright-core is a devDependency of client/ — resolve it from there.
const require = createRequire(join(repoRoot, 'client', 'package.json'));
const { chromium } = require('playwright-core');

const BASE_URL = process.env.BASE_URL || 'http://localhost:2099';
const mode = process.argv[2] || 'smoke';
const prompt = process.argv[3] || 'brushed copper';

async function launchPage() {
	let browser;
	try {
		browser = await chromium.launch({ channel: 'msedge', headless: true });
	} catch {
		browser = await chromium.launch({ channel: 'chrome', headless: true });
	}
	const page = await (await browser.newContext({ viewport: { width: 1600, height: 900 } })).newPage();
	const issues = [];
	page.on('pageerror', (err) => issues.push(`[pageerror] ${err.message}`));
	page.on('console', (m) => {
		// ANGLE shader precision warnings (X4122) are benign noise on Windows.
		if (m.type() === 'error' && !m.text().includes('X4122')) issues.push(`[console] ${m.text()}`);
	});
	return { browser, page, issues };
}

async function openApp(page) {
	await page.goto(BASE_URL + '/', { waitUntil: 'networkidle' });
	await page.waitForSelector('#viewer-3d canvas', { timeout: 20000 });
	await page.waitForTimeout(6000); // GLTF loads + first render
}

async function smoke() {
	const { browser, page, issues } = await launchPage();
	await openApp(page);
	const shot = join(shotsDir, 'smoke.png');
	await page.screenshot({ path: shot });
	console.log('screenshot:', shot);
	report(issues);
	await browser.close();
}

async function generate() {
	const { browser, page, issues } = await launchPage();
	await openApp(page);

	await page.fill('input[placeholder*="Type in a material"]', prompt);
	const buttons = page.locator('button', { hasText: 'Generate' });
	let clicked = false;
	for (let i = 0; i < (await buttons.count()); i++) {
		const text = (await buttons.nth(i).innerText()).trim();
		if (/^Generate\b/.test(text) && !text.includes('Similar')) {
			await buttons.nth(i).click();
			clicked = true;
			break;
		}
	}
	if (!clicked) throw new Error('Generate button not found');

	// First run loads SD-Turbo (~10s warm, minutes on a cold weight download).
	await page.waitForSelector('img[src*="gen_images/generated"]', { timeout: 300000 });
	await page.waitForTimeout(1500);
	const shot = join(shotsDir, 'generate.png');
	await page.screenshot({ path: shot });
	const imgs = await page.$$eval('img[src*="gen_images/generated"]', (els) =>
		els.map((el) => ({ src: el.src.split('/').pop(), loaded: el.naturalWidth > 0 })));
	console.log('generated:', JSON.stringify(imgs, null, 1));
	console.log('screenshot:', shot);
	if (!imgs.length || imgs.some((i) => !i.loaded)) throw new Error('generated images missing/broken');
	report(issues);
	await browser.close();
}

function report(issues) {
	if (issues.length) {
		console.error('PAGE ISSUES:\n' + issues.join('\n'));
		process.exitCode = 1;
	} else {
		console.log('page issues: none');
	}
}

const modes = { smoke, generate };
if (!modes[mode]) {
	console.error(`unknown mode '${mode}' — use: smoke | generate "<prompt>"`);
	process.exit(2);
}
modes[mode]().catch((err) => {
	console.error('DRIVER FAILED:', err.message);
	process.exit(1);
});

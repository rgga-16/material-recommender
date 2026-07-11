import { describe, expect, it } from 'vitest';
import { imageUrl } from './api.js';

describe('imageUrl', () => {
	it('prefixes public paths with a slash', () => {
		expect(imageUrl('gen_images/x.png')).toBe('/gen_images/x.png');
	});

	it('normalizes backslashes and duplicate leading slashes', () => {
		expect(imageUrl('gen_images\\renderings\\current\\x.png'))
			.toBe('/gen_images/renderings/current/x.png');
		expect(imageUrl('/gen_images/x.png')).toBe('/gen_images/x.png');
	});

	it('encodes spaces', () => {
		expect(imageUrl('gen_images/oak wood_0.png')).toBe('/gen_images/oak%20wood_0.png');
	});

	it('passes through data/blob/http URLs untouched', () => {
		expect(imageUrl('data:image/png;base64,AAAA')).toBe('data:image/png;base64,AAAA');
		expect(imageUrl('blob:http://x/y')).toBe('blob:http://x/y');
		expect(imageUrl('https://example.com/a.png')).toBe('https://example.com/a.png');
	});

	it('passes through empty values', () => {
		expect(imageUrl(null)).toBe(null);
		expect(imageUrl('')).toBe('');
	});

	it('appends a cache buster when asked', () => {
		expect(imageUrl('gen_images/x.png', { bust: true })).toMatch(/^\/gen_images\/x\.png\?v=\d+$/);
	});
});

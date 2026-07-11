import { beforeEach, describe, expect, it } from 'vitest';
import { createSelection } from './selection.js';

function makeInfos() {
	// two chairs (frame + backrest each) and a floor
	const infos = [];
	for (const parent of ['chair1', 'chair2']) {
		for (const name of ['frame', 'backrest']) {
			const info = { name, parent, is_selectable: true };
			info.mesh = { model_name: name, model_parent: parent, material: {} };
			infos.push(info);
		}
	}
	const floor = { name: 'floor', parent: 'floor', is_selectable: true };
	floor.mesh = { model_name: 'floor', model_parent: 'floor', material: {} };
	infos.push(floor);
	return infos;
}

describe('createSelection', () => {
	let infos, selection, changes;

	beforeEach(() => {
		infos = makeInfos();
		changes = [];
		selection = createSelection({
			getInfos: () => infos,
			onChange: (sel) => changes.push(sel),
		});
	});

	const meshOf = (parent, name) =>
		infos.find((i) => i.parent === parent && i.name === name).mesh;

	it('plain click selects exactly one part', () => {
		selection.click(meshOf('chair1', 'frame'));
		selection.click(meshOf('chair1', 'backrest'));
		expect(selection.infos.map((i) => [i.parent, i.name])).toEqual([['chair1', 'backrest']]);
	});

	it('plain click on a selected part deselects it', () => {
		selection.click(meshOf('floor', 'floor'));
		selection.click(meshOf('floor', 'floor'));
		expect(selection.infos).toEqual([]);
	});

	it('shift-click adds to the selection', () => {
		selection.click(meshOf('chair1', 'frame'));
		selection.click(meshOf('chair2', 'frame'), { shift: true });
		expect(selection.infos).toHaveLength(2);
	});

	it('ctrl-click selects every part of the object', () => {
		selection.click(meshOf('chair1', 'frame'), { ctrl: true });
		const selected = selection.infos.map((i) => `${i.parent}/${i.name}`).sort();
		expect(selected).toEqual(['chair1/backrest', 'chair1/frame']);
	});

	it('alt-click selects same-named parts across numbered siblings', () => {
		selection.click(meshOf('chair1', 'frame'), { alt: true });
		const selected = selection.infos.map((i) => `${i.parent}/${i.name}`).sort();
		expect(selected).toEqual(['chair1/frame', 'chair2/frame']);
	});

	it('clear empties the selection and notifies', () => {
		selection.click(meshOf('chair1', 'frame'));
		selection.clear();
		expect(selection.infos).toEqual([]);
		expect(changes.at(-1)).toEqual([]);
	});
});

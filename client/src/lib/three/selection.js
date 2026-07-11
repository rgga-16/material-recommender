// Selection state for scene parts. One code path handles all click modes —
// the old component duplicated the select/deselect logic across the
// shift/ctrl/alt branches.
//
// Click semantics (unchanged from the legacy viewport):
//   plain  — select only the clicked part (or deselect it if selected)
//   shift  — add the clicked part to the selection
//   alt    — also select all parts with the same base name (digits stripped)
//            under parents with the same base name
//   ctrl   — also select every part of the same parent object

function baseName(s) {
	return String(s || '').replace(/\d+/g, '');
}

export function createSelection({ getInfos, onChange }) {
	let selectedInfos = [];

	function notify() {
		onChange([...selectedInfos]);
	}

	function meshes() {
		return selectedInfos.map((info) => info.mesh);
	}

	function isSelected(info) {
		return selectedInfos.includes(info);
	}

	function infoForMesh(mesh) {
		return getInfos().find(
			(item) => item.name === mesh.model_name && item.parent === mesh.model_parent
		) || null;
	}

	function add(info) {
		if (info && info.mesh && !isSelected(info)) selectedInfos.push(info);
	}

	function addGroup(clickedInfo, { sameName }) {
		const nameKey = baseName(clickedInfo.name);
		const parentKey = sameName ? baseName(clickedInfo.parent) : clickedInfo.parent;
		for (const info of getInfos()) {
			const parentMatches = sameName
				? baseName(info.parent) === parentKey
				: info.parent === parentKey;
			if (parentMatches && (!sameName || baseName(info.name) === nameKey)) {
				add(info);
			}
		}
	}

	function clear() {
		selectedInfos = [];
		notify();
	}

	/** Handle a click on a part's mesh. Returns the selected infos. */
	function click(mesh, { shift = false, ctrl = false, alt = false } = {}) {
		const info = infoForMesh(mesh);
		if (!info) return selectedInfos;

		if (!isSelected(info)) {
			if (!shift && !ctrl && !alt) selectedInfos = [];
			add(info);
			if (alt) addGroup(info, { sameName: true });
			else if (ctrl) addGroup(info, { sameName: false });
		} else if (alt) {
			addGroup(info, { sameName: true });
		} else if (ctrl) {
			addGroup(info, { sameName: false });
		} else {
			selectedInfos = selectedInfos.filter((item) => item !== info);
		}
		notify();
		return selectedInfos;
	}

	return {
		click,
		clear,
		meshes,
		get infos() {
			return selectedInfos;
		},
	};
}

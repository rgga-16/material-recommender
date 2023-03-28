import { writable } from 'svelte/store';

export const curr_rendering_path = writable(""); 
export const curr_textureparts_path = writable(""); 
export const curr_texture_parts = writable({});
export const saved_color_palettes = writable([
    {
        name: "Default",
        palette: [
            "#FFFFFF",
            "#FFFFFF",
            "#FFFFFF",
            "#FFFFFF",
            "#FFFFFF",
        ],
    }
]);

export const actions_panel_tab = writable("generate");
export const information_panel_tab = writable("information");
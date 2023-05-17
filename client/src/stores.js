import { writable } from 'svelte/store';

export const curr_rendering_path = writable(""); 
export const curr_textureparts_path = writable(""); 
export const curr_texture_parts = writable({});

export const models_setup_path = writable("");
export const models_setup = writable({});

export const selected_obj_name = writable(null); //Keeps track of the selected part's object in the 3D view
export const selected_part_name = writable(null); //Keeps track of the name of the currently selected part in the 3D view


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

export const actions_panel_tab = writable("chatbot"); //Keeps track of which tab is currently selected in the actions panel
export const information_panel_tab = writable("details"); //Keeps track of which tab is currently selected in the information panel

export const generate_tab_page = writable(0); //Keeps track of which page is currently selected in the generate tab
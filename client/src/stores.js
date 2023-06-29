import { writable } from 'svelte/store';

export const curr_rendering_path = writable(""); 
export const curr_textureparts_path = writable(""); 
export const curr_texture_parts = writable({});

export const models_setup_path = writable("");
export const models_setup = writable({});

export const chatbot_input_message = writable(""); //Keeps track of the input message in the chatbot

export const design_brief = writable(`
Design Brief: Modern Minimalist Master Bedroom for a Filipino Couple
Demographics
The clients are a Filipino couple in their early 30s who live in the bustling city of Manila in the Philippines. They are both working professionals who want a cozy bedroom to relax and unwind after a busy day.

Project Background
The project background is to create a modern minimalist design with warm, inviting tones that are reflective of the clients' lifestyle. The design should have a mix of contemporary and traditional elements.

Preferred Design Style
The preferred design style for the bedroom is modern minimalist with a touch of Scandinavian aesthetic. It should have a neutral color palette with accents of natural, warm wood textures and matte finishes.

Desired Ambience and Feel
The desired ambience and feel for the bedroom should be calm, soothing, and relaxing. The lighting should be soft and warm with a cozy, intimate atmosphere.

Client's Preferences
The clients prefer a minimalistic design with clean lines and geometric shapes. They also have a preference for natural materials such as wood in their bedroom. They would also prefer a high-quality mattress, a comfortable duvet, and pillows with a thread count of 400 or higher.

Budget
The budget of the project is around PHP 100,000. This is a moderate budget that should cover the cost of furnishings and decorations.

Furniture and Accessories
The bedroom will contain the following furniture and accessories:

A queen-size, low-lying platform bed with wood headboard and built-in sidetables on each side.
Two white, matte-finished drawers and a cabinet with wood accents.
A 32-inch TV.
A neutral, textured carpet.
Soft, light-colored curtains that allow natural light into the room.
Several floating shelves to display photo frames and books.
Pottery planters with easy-to-maintain indoor plants, a few books, and a set of Bang & Olufsen headphones.
Planned Uses
The planned uses of the bedroom are for sleeping, relaxation, and lounging. The built-in sidetables on each side of the bed provide ample storage for books, tablets, and devices. The floating shelves will be used to display interiors book collections.

Location
The bedroom is located within the city of Manila, by the bay area in a high-rise condominium. The environment is urban, busy, and modern. But the design approach aims to offset the busy environment by creating a relaxing space that almost feels like a retreat or sanctuary - where the couple could spend their downtime, escaping from the hectic energy of the city.
`); //Keeps track of the design brief

// selected_objs_and_parts = [
//     { part_name: "part1", 
//       obj_name: "obj1",
//       mat_metallic: 0.5, //THREE.MeshStandardMaterial.metalness
//       mat_roughness: 0.5, //THREE.MeshStandardMaterial.roughness
//       mat_transparent: false, //THREE.MeshStandardMaterial.transparent
//       mat_opacity: 1, //THREE.MeshStandardMaterial.opacity
//       texture_url: "texture1", //THREE.MeshStandardMaterial.map
//       color: "color1" //THREE.MeshStandardMaterial.color
//     },...
//     {
//         part_name: "partn",
//          obj_name: "objn" ....
//      }
// ]
export const selected_objs_and_parts =writable ([]); //Keeps track of the selected parts and their parent objects in the 3D view
export const objects_3d = writable([]); //Keeps track of all of the objects in the 3D view


export const selected_obj_name = writable(null); //Keeps track of the selected part's object in the 3D view
export const selected_part_name = writable(null); //Keeps track of the name of the currently selected part in the 3D view

//Keeps track of the URL of the image texture that is being dragged and transferred. 
// This URL is used to display the texture map in the 3D view.
export const transferred_texture_url = writable(""); 

// Keeps track of the URL of the image texture being dragged and transferred.
// This URL is used to display the texture map as an image in HTML.
export const transferred_textureimg_url =writable("");

//Keeps track of the name of the image texture being dragged and transferred
export const transferred_texture_name = writable(""); 

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

export const actions_panel_tab = writable("generate"); //Keeps track of which tab is currently selected in the actions panel
export const information_panel_tab = writable("details"); //Keeps track of which tab is currently selected in the information panel
export const display_panel_tab = writable("3d_display")

export const generate_module = writable(); //Keeps track of the generate module. Used if you want to call the module to generate something.

export const generate_tab_page = writable(0); //Keeps track of which page is currently selected in the generate tab

export const displayWidth =writable(0); //Keeps track of the width of the display div which contains the Rendering View and 3D View
export const displayHeight = writable(0); //Keeps track of the height of the display div which contains the Rendering View and 3D View

export const isDraggingImage = writable(false); //Keeps track of whether an image is currently being dragged and transferred or not
export const generated_texture_name = writable(""); //Keeps track of the name of the generated texture


export let in_japanese = writable(false); //Keeps track of whether the language is in Japanese or not
export let use_chatgpt = writable(false); //Keeps track of whether the app uses chatgpt or not
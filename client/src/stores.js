import { writable } from 'svelte/store';

export const curr_rendering_path = writable(""); 
export const curr_textureparts_path = writable(""); 
export const curr_texture_parts = writable({});

export const models_setup_path = writable("");
export const models_setup = writable({});

export const chatbot_input_message = writable(""); //Keeps track of the input message in the chatbot

export const design_brief = writable(`
Design Brief for an Interior Bedroom

Project Overview: The project is to design an interior bedroom for a young couple who just moved in to a newly-built condominium unit in Bonifacio Global City (BGC), Taguig, Philippines. The bedroom should be a comfortable and stylish space that reflects their personalities and taste. The couple prefers a modern and minimalist design with a touch of warmth and elegance.

Design Objectives: Create a functional and comfortable space for the couple to relax and sleep in. Incorporate a modern and minimalist design style with a touch of warmth and elegance. Use a color scheme that is soothing and relaxing with pops of bold color to add interest and personality. Maximize storage space to keep the room organized and clutter-free. Incorporate lighting that is both functional and decorative. Use sustainable and eco-friendly materials wherever possible.

Design Elements Location: The interior bedroom will be located in a newly-built condominium situated in Bonifacio Global City (BGC), Taguig, Philippines.

Color Scheme: The color scheme for the bedroom should be soothing and relaxing, with pops of bold color to add interest. The walls should be painted in a light shade of beige or white, while the bedding and curtains can be in a darker shade of gray or navy blue. Bold pops of color can be added through decorative pillows, artwork, and accessories.

Furniture: The bedroom should have a queen-sized bed with a stylish headboard and luxurious linens. A bedside table with a lamp should be placed on either side of the bed. A sleek dresser with drawers and a mirror should be placed against one wall, while a comfortable yet stylish armchair can be placed in one corner for reading or relaxing.

Storage: The bedroom should have ample storage space to keep the room organized and clutter-free. The dresser should have enough drawers to store clothing, while a built-in closet with shelves and hanging space should be included for additional storage.

Lighting: The bedroom should have both functional and decorative lighting. A sleek pendant light or chandelier can be used for general lighting, while bedside lamps can be used for reading. A stylish floor lamp with a decorative shade can be placed in a corner for additional lighting.

Materials: Sustainable and eco-friendly materials should be used wherever possible. The flooring can be made of bamboo or wood, while the bedding can be made of organic cotton. The furniture can be made of FSC certified wood or recycled materials. The lighting fixtures can be energy-efficient LED bulbs.

Conclusion: The interior bedroom design should be a comfortable and stylish space that reflects the couple's personalities and taste. The design should incorporate a modern and minimalist style with a touch of warmth and elegance. The color scheme should be soothing with pops of bold color, and ample storage space should be included to keep the room organized and clutter-free. Sustainable and eco-friendly materials should be used wherever possible. The interior bedroom will be located in a newly-built condominium situated in Bonifacio Global City (BGC), Taguig, Philippines.
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

export const actions_panel_tab = writable("chatbot"); //Keeps track of which tab is currently selected in the actions panel
export const information_panel_tab = writable("details"); //Keeps track of which tab is currently selected in the information panel
export const display_panel_tab = writable("3d_display")

export const generate_module = writable(); //Keeps track of the generate module. Used if you want to call the module to generate something.

export const generate_tab_page = writable(0); //Keeps track of which page is currently selected in the generate tab

export const displayWidth =writable(0); //Keeps track of the width of the display div which contains the Rendering View and 3D View
export const displayHeight = writable(0); //Keeps track of the height of the display div which contains the Rendering View and 3D View

export const isDraggingImage = writable(false); //Keeps track of whether an image is currently being dragged and transferred or not
export const generated_texture_name = writable(""); //Keeps track of the name of the generated texture
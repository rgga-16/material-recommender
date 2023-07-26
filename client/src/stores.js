import { writable } from 'svelte/store';

export const curr_rendering_path = writable(""); 
export const curr_textureparts_path = writable(""); 
export const curr_texture_parts = writable({});
export const japanese_curr_texture_parts = writable({});

export const models_setup_path = writable("");
export const models_setup = writable({});

export const chatbot_input_message = writable(""); //Keeps track of the input message in the chatbot

export const design_brief = writable(`
Design Brief for a Family Poolside Patio

Client Demographics: The clients are a family of four with two young children. They live in a coastal area in the Philippines and love spending time outdoors. They want to create a poolside patio that is both functional and stylish, where the whole family can relax and have fun.

Background: The family recently had a pool installed in their backyard and wants to create a poolside patio that complements the pool and provides them with a space to entertain guests and spend time as a family.

Preferred Design Style: The family prefers a coastal design style with natural textures, light colors, and a relaxed vibe. They want the design to be cohesive with their home's coastal interior design, which features a lot of white and blue hues.

Desired Feel and Ambience: The family wants the poolside patio to have a fun and relaxed feel, with a touch of sophistication. They want the space to be perfect for both daytime and nighttime use, with soft lighting that creates a cozy and inviting atmosphere.

Colors, Materials, and Finishes: The family prefers a color scheme that is light and airy, with shades of blue and green to complement the pool. They want the materials and finishes to be durable and low-maintenance, while also being natural.

Budget: The budget for the project is moderate.

Furniture:
Four patio lounge chairs
Two patio sidetables
Two outdoor umbrellas
An outdoor sofa
Two outdoor sofa chairs
A coffee table
An outdoor pool
Outdoor flooring
An outdoor dining table
Five outdoor dining chairs

Planned Uses: The poolside patio will be used for entertaining guests, lounging by the pool, and dining al fresco. The lounge chairs and umbrellas will be used for sunbathing and relaxing by the pool, while the outdoor sofa and chairs will be used for lounging and socializing. The dining table and chairs will be used for outdoor dining, and the coffee table will be used for drinks and snacks.

Location: The poolside patio will be located in a coastal area in the Philippines. The environment will be tropical, with a lot of greenery and a warm climate. The design will take inspiration from the coastal surroundings, with natural textures and colors that blend in with the environment.
`); //Keeps track of the design brief

// selected_objs_and_parts = [
//     { part_name: "part1", 
//       obj_name: "obj1",
//       mat_metallic: 0.5, //THREE.MeshStandardMaterial.metalness
//       roughness: 0.5, //THREE.MeshStandardMaterial.roughness
//       mat_transparent: false, //THREE.MeshStandardMaterial.transparent
//       opacity: 1, //THREE.MeshStandardMaterial.opacity
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
export const display_panel_tab = writable("3d_display");

export const generate_module = writable(); //Keeps track of the generate module. Used if you want to call the module to generate something.

export const generate_tab_page = writable(0); //Keeps track of which page is currently selected in the generate tab

export const displayWidth =writable(0); //Keeps track of the width of the display div which contains the Rendering View and 3D View
export const displayHeight = writable(0); //Keeps track of the height of the display div which contains the Rendering View and 3D View

export const isDraggingImage = writable(false); //Keeps track of whether an image is currently being dragged and transferred or not
export const generated_texture_name = writable(""); //Keeps track of the name of the generated texture
export let in_japanese = writable(false); //Keeps track of whether the language is in Japanese or not
export let use_chatgpt = writable(false); //Keeps track of whether the app uses chatgpt or not

/* 
action_history = [
    {
        "name": "action_name",
        "object": "object_name",
        "part": "part_name",
        "properties": {
            "property1": {
                "old": "old_value",
                "new": "new_value"
            },
            "property2": {
                "old": "old_value",
                "new": "new_value"
            },
        }
    }
]
*/
export let action_history = writable({
    actions: [],
    currentIndex: -1
}); //Keeps track of the action history

export let threed_display_global = writable(null); //Keeps track of the 3D display. Can call the functions in the 3D display module
export let information_panel_global = writable(null); //Keeps track of the information panel. Can call the functions in the information panel module
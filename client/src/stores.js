import { writable } from 'svelte/store';

export const curr_rendering_path = writable(""); 
export const curr_textureparts_path = writable(""); 
export const curr_texture_parts = writable({});
export const japanese_curr_texture_parts = writable({});

export const models_setup_path = writable("");
export const models_setup = writable({});

export const chatbot_input_message = writable(""); //Keeps track of the input message in the chatbot

export const design_brief = writable(`
Design Brief: Bedroom Design for a Modern Urban Dweller

Demographics and Target Market: The client is a young professional in their late 20s, working in a creative industry. They have a busy lifestyle and value comfort, functionality, and aesthetics. The target market includes individuals who appreciate contemporary design and seek a peaceful retreat within their urban living space.

Background of the Project: The project aims to create a stylish and functional bedroom that reflects the client's personality and provides a serene sanctuary amidst the bustling city life. The design should incorporate elements that cater to the client's needs and preferences while complementing their modern lifestyle.

Preferred Design Style: The preferred design style for the bedroom is a blend of modern and minimalist aesthetics. Clean lines, sleek furniture, and a neutral color palette will be used to create a calming and sophisticated atmosphere.

Desired Feel and Ambience: The client desires a tranquil and cozy atmosphere in the bedroom. The space should evoke a sense of relaxation, allowing them to unwind after a long day. The ambience should be warm, inviting, and conducive to restful sleep.

Budget: The client has a moderate budget for the project, allowing for quality materials and furnishings without excessive extravagance.

Furniture and Accessories: The bedroom will include the following furniture and accessories:
Bed: A queen-sized bed with pillows, a comfortable mattress, a cozy blanket, a throw blanket, a sleek bedframe, and a padded headboard. The bed will feature built-in sidetables on each side.
Two closed drawers: These drawers will provide storage for clothing and personal items, maintaining a clutter-free environment.
An open drawer: This drawer will serve as a display area for decorative items or books.
TV: A wall-mounted TV will be positioned for comfortable viewing from the bed.
Carpet: A plush, neutral-colored carpet will cover the bedroom floor, adding warmth and comfort.
Curtains: Floor-to-ceiling curtains in a light fabric will be installed to control natural light and provide privacy.
Shelves: Minimalist floating shelves will be mounted on the walls to showcase books, potted plants, and decorative accessories.
Accessories: Potted plants, books, figurines, and headphones will be strategically placed to add personal touches and enhance the overall ambiance.

Planned Uses of the Bedroom: The bedroom will serve as a multifunctional space, primarily for relaxation, sleep, and personal rejuvenation. It will also provide a cozy reading nook, a small entertainment area for watching TV, and a display space for the client's favorite books and decorative items.

Location: The bedroom is located in a modern urban apartment in a bustling city. The environment is vibrant and dynamic, and the design should create a peaceful oasis within this energetic setting. The city is fictional, allowing for creative freedom in designing the bedroom to suit various urban locations.

Please note that the design brief is flexible and can be further refined based on the client's specific requirements and preferences.
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
    // {
    //     name: "Default",
    //     palette: [
    //         "#FFFFFF",
    //         "#FFFFFF",
    //         "#FFFFFF",
    //         "#FFFFFF",
    //         "#FFFFFF",
    //     ],
    // }
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
export let use_chatgpt = writable(true); //Keeps track of whether the app uses chatgpt or not

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
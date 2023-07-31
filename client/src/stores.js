import { writable } from 'svelte/store';

export const curr_rendering_path = writable(""); 
export const curr_textureparts_path = writable(""); 
export const curr_texture_parts = writable({});
export const japanese_curr_texture_parts = writable({});

export const models_setup_path = writable("");
export const models_setup = writable({});

export const chatbot_input_message = writable(""); //Keeps track of the input message in the chatbot

export const design_brief = writable(`
家族向けプールサイド パティオのデザイン ブリーフ

顧客層: 顧客は 2 人の幼い子供を持つ 4 人家族です。 彼らはフィリピンの沿岸地域に住んでおり、屋外で時間を過ごすのが大好きです。 彼らは、家族全員がリラックスして楽しめる、機能的でスタイリッシュなプールサイド パティオを作りたいと考えています。

背景: この家族は最近裏庭にプールを設置しましたが、プールを補完し、ゲストを楽しませたり、家族で過ごすためのスペースを提供するプールサイド パティオを作りたいと考えています。

好みのデザインスタイル：家族は、自然な質感、明るい色、リラックスした雰囲気を備えた海岸沿いのデザインスタイルを好みます。 彼らは、白と青の色合いを多用した海岸沿いの自宅のインテリア デザインとデザインが調和することを望んでいます。

望ましい雰囲気と雰囲気: 家族は、プールサイドのパティオが楽しくてリラックスした雰囲気でありながら、洗練された雰囲気であることを望んでいます。 彼らは、居心地の良い魅力的な雰囲気を作り出す柔らかい照明を備えた、昼と夜の両方の使用に最適な空間を望んでいます。

色、素材、仕上げ: 家族は、プールを引き立てる青と緑の色合いで、明るく風通しの良い配色を好みます。 彼らは、素材と仕上げが耐久性があり、メンテナンスの手間がかからず、同時に自然であることを望んでいます。

予算: プロジェクトの予算は中程度です。

家具：
パティオラウンジチェア8脚
パティオサイドテーブル 4 台
アウトドアパラソル4本
屋外用ソファ
屋外ソファチェア 2 脚
コーヒーテーブル
屋外プール
屋外床材
屋外のダイニングテーブル
屋外用ダイニングチェア 6脚

計画された用途: プールサイドのパティオは、ゲストのおもてなし、プールサイドでのくつろぎ、屋外での食事に使用されます。 ラウンジチェアとパラソルは、日光浴やプールサイドでのリラックスに使用され、屋外のソファと椅子はくつろぎや社交に使用されます。 ダイニングテーブルと椅子は屋外での食事に使用され、コーヒーテーブルはドリンクや軽食に使用されます。

場所: プールサイド パティオはフィリピンの沿岸地域に位置します。 環境は緑が多く、気候が温暖な熱帯になります。 デザインは海岸環境からインスピレーションを得ており、環境に溶け込む自然な質感と色を採用しています。
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
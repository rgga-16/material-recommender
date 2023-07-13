import { writable } from 'svelte/store';

export const curr_rendering_path = writable(""); 
export const curr_textureparts_path = writable(""); 
export const curr_texture_parts = writable({});
export const japanese_curr_texture_parts = writable({});

export const models_setup_path = writable("");
export const models_setup = writable({});

export const chatbot_input_message = writable(""); //Keeps track of the input message in the chatbot

export const design_brief = writable(`
デザイン概要: 日本人夫婦のためのモダンなミニマリスト主寝室
人口動態
クライアントは、日本の賑やかな都市東京に住む30代前半の日本人夫婦です。 彼らは二人とも働くプロフェッショナルで、忙しい一日の後にリラックスできる居心地の良いベッドルームを望んでいます。

プロジェクトの背景
プロジェクトの背景は、クライアントのライフスタイルを反映した温かみのある魅力的な色調を備えたモダンなミニマリスト デザインを作成することです。 デザインには現代的な要素と伝統的な要素が混在している必要があります。

好みのデザインスタイル
寝室に好まれるデザインスタイルは、スカンジナビアの美学を加えたモダンなミニマリストです。

求める雰囲気や雰囲気
寝室に求められる雰囲気と雰囲気は、穏やかで、心地よく、リラックスできるものでなければなりません。 照明は柔らかくて温かみのある、居心地の良い親密な雰囲気でなければなりません。

クライアントの好み
クライアントは、すっきりとしたラインと幾何学的な形状を備えたミニマルなデザインを好みます。 また、寝室には木材などの天然素材を好む傾向があります。

バジェット
プロジェクトの予算は約10万ペソです。 これは、家具や装飾品の費用をカバーできる適度な予算です。

家具と付属品
ベッドルームには次の家具とアクセサリーが含まれます。
クイーンサイズの低めのプラットフォームベッドで、木製のヘッドボードと両側にサイドテーブルが組み込まれています。
マット仕上げの白い引き出し 2 つと木のアクセントが付いたキャビネット。
32インチのテレビです。
ニュートラルな質感のカーペット。
自然光を部屋に取り込む、柔らかく明るい色のカーテン。
フォトフレームや本を展示するためのいくつかのフローティングシェルフ。
手入れが簡単な屋内植物を備えた陶器のプランター、数冊の本、Bang & Olufsen のヘッドフォンのセット。
計画された用途
寝室の計画的な用途は、睡眠、リラクゼーション、くつろぎです。 ベッドの両側に組み込まれたサイドテーブルには、本、タブレット、デバイスを十分に収納できます。 フローティングシェルフはインテリアの書籍コレクションを展示するために使用されます。

位置
ベッドルームは東京都内の湾岸エリアにある高層マンションにあります。 環境は都会的で、賑やかで、モダンです。 しかし、デザインアプローチは、カップルが都市の多忙なエネルギーから逃れて休憩時間を過ごすことができる、まるで隠れ家か聖域のように感じるリラックスできる空間を作り出すことで、忙しい環境を相殺することを目指しています。
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
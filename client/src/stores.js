import { writable } from 'svelte/store';

export const curr_rendering_path = writable(""); 
export const curr_textureparts_path = writable(""); 
export const curr_texture_parts = writable({});
export const japanese_curr_texture_parts = writable({});

export const models_setup_path = writable("");
export const models_setup = writable({});

export const chatbot_input_message = writable(""); //Keeps track of the input message in the chatbot

export const design_brief = writable(`
デザイン概要: 現代の都市生活者のための寝室のデザイン

人口統計とターゲット市場: クライアントは、クリエイティブ業界で働く 20 代後半の若い専門家です。 彼らは忙しいライフスタイルを送っており、快適さ、機能性、美しさを重視しています。 ターゲット市場には、現代的なデザインを高く評価し、都市の生活空間の中で静かな隠れ家を求める人々が含まれます。

プロジェクトの背景: このプロジェクトは、クライアントの個性を反映し、都会の喧騒の中に静かな安息の場を提供する、スタイリッシュで機能的なベッドルームを作成することを目的としています。 デザインには、クライアントの現代のライフスタイルを補完しながら、クライアントのニーズや好みに応える要素を組み込む必要があります。

推奨されるデザイン スタイル: ベッドルームに推奨されるデザイン スタイルは、モダンとミニマリストの美学を組み合わせたものです。 すっきりとしたライン、洗練された家具、中間色を使用し、落ち着いた洗練された雰囲気を作り出しています。

希望する感触と雰囲気: クライアントは寝室に静かで居心地の良い雰囲気を望んでいます。 空間はリラックスした感覚を呼び起こし、長い一日の後にリラックスできるようにする必要があります。 雰囲気は暖かく、魅力的で、安らかな眠りにつながるものでなければなりません。

好みの色、素材、仕上げ: クライアントは、ベージュ、トープ、ソフト グレーなどのアースカラーを中心としたニュートラルな配色を好みます。 彼らは木や石などの天然素材だけでなく、リネンやベルベットなどの質感を好みます。 仕上げはマットで控えめにする必要があり、全体的なミニマリストの美しさに貢献します。

予算: クライアントはプロジェクトに対して適度な予算を持っており、過剰な贅沢をせずに高品質の素材や家具を使用できます。

家具と付属品: ベッドルームには次の家具と付属品が含まれます。
ベッド: 枕付きのクイーンサイズのベッド、快適なマットレス、心地よい毛布、掛け毛布、洗練されたベッドフレーム、パッド入りのヘッドボード。 ベッドの両側にサイドテーブルが組み込まれています。
2 つの閉じた引き出し: これらの引き出しは衣類や身の回り品を保管し、整理整頓された環境を維持します。
開いた引き出し: この引き出しは、装飾品や書籍の展示エリアとして機能します。
テレビ：ベッドから快適に視聴できるように壁掛けテレビを設置します。
カーペット：豪華なニュートラルカラーのカーペットが寝室の床を覆い、暖かさと快適さを加えます。
カーテン：自然光を制御しプライバシーを確保するために、軽い生地の床から天井までのカーテンが設置されます。
棚: ミニマリストのフローティングシェルフが壁に取り付けられ、書籍、鉢植え、装飾アクセサリーを展示します。
アクセサリー: 鉢植え、本、置物、ヘッドフォンを戦略的に配置して、個人的なタッチを加え、全体の雰囲気を高めます。

寝室の計画された用途: 寝室は、主にリラクゼーション、睡眠、個人のリフレッシュのための多機能スペースとして機能します。 また、居心地の良い読書コーナー、テレビを見るための小さなエンターテイメントエリア、クライアントのお気に入りの本や装飾品を展示するスペースも提供します。

場所: ベッドルームは、賑やかな都市にあるモダンな都会のアパートにあります。 環境は活気に満ち、ダイナミックであり、デザインはこのエネルギッシュな環境の中に平和なオアシスを生み出す必要があります。 都市は架空のものであるため、都市のさまざまな場所に合わせて寝室を創造的に自由にデザインできます。

設計概要は柔軟であり、クライアントの特定の要件や好みに基づいてさらに調整できることに注意してください。
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
export let in_japanese = writable(true); //Keeps track of whether the language is in Japanese or not
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
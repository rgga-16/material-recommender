import { writable } from 'svelte/store';

export const curr_rendering_path = writable(""); 
export const curr_textureparts_path = writable(""); 
export const curr_texture_parts = writable({});
export const japanese_curr_texture_parts = writable({});

export const models_setup_path = writable("");
export const models_setup = writable({});

export const chatbot_input_message = writable(""); //Keeps track of the input message in the chatbot

export const design_brief = writable(`
通常の家庭用バスルームのデザイン概要


クライアントプロフィール
クライアントは、アメリカ・シアトルの郊外に住む中年の夫婦です。彼らは共に働くプロフェッショナルで、家のデザインにおいて機能性とシンプルさを重視しています。2人の十代の子供がおり、頻繁にゲストを招くため、バスルームは様々なユーザーに対応できる必要があります。

プロジェクトの背景 
この家族は最近新しい家を購入し、既存のバスルームを自分たちのニーズと美的嗜好に合うように改装することを考えています。現在のバスルームは機能的ではありますが、彼らが求める暖かさと招き入れる感じが欠けています。家族は、実用的で、メンテナンスが容易で、時代を超えた魅力を持つデザインを求めています。

デザインスタイル
バスルームのデザインスタイルはモダンミニマリズムが好ましいです。このスタイルは、クリーンなライン、シンプルな色合い、 clutterのない特徴があります。デザインは機能性と使いやすさに焦点を当て、過度に装飾的または複雑な要素を避けるべきです。

雰囲気
バスルームの雰囲気は、落ち着いた、穏やかなものが望ましいです。この空間は、日常生活の忙しさからの隠れ家のように感じられるべきで、家族がリラックスし、リフレッシュできる場所であるべきです。自然光、柔らかい色、シンプルで整理された空間の使用が、この雰囲気を作り出すのに役立ちます。

予算
このプロジェクトの予算は適度です。家族は品質の高い材料と設備に投資する意思がありますが、コスト効率と価値に対する考慮が重要です。

家具とアクセサリー
バスルームには以下のアイテムが含まれます：

バスルームの床
壁の換気口
タオルホルダー（大きなタオルと小さなタオルを保持）
壁のライトスイッチ
壁のソケット
シンク
トイレ
バスタブ
バスタブの蛇口
シャワーカーテン
シャワーカーテンロッド
トイレットペーパーホルダー（トイレットペーパーロールを保持）
バスルームマット
鏡（フレーム付き）

計画された使用法 
このバスルームは、入浴、歯磨き、トイレの使用などの日常的な衛生習慣のために使用されます。また、リラクゼーションの場としても機能し、バスタブは浸かってリラックスするために使用されます。洗面台エリアは、髭剃りや化粧をするなどの身だしなみの活動のために使用されます。バスルームはゲストを収容する必要もあり、清掃とメンテナンスが容易であるべきです。

場所
バスルームは、アメリカ・シアトルの郊外の家の2階に位置しています。家は静かな近所にあり、モダンと伝統的な家が混在しています。バスルームには窓が1つあり、自然光と換気を提供します。シアトルの気候は温暖で、冬は穏やかで湿気があり、夏は暖かく乾燥しています。これは、バスルームの材料と仕上げを選ぶ際に考慮すべき事項です。

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
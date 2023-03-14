
import os 
import openai
openai.api_key=os.getenv("OPENAI_API_KEY") #If first time using this repo, set the environment variable "OPENAI_API_KEY", to your API key from OPENAI
import re , ast
import yake 

kw_extractor = yake.KeywordExtractor(lan='en',n=3,top=20,dedupLim=0.9)


def parse_into_list(string):
    items = []
    for match in re.findall(r'\d+\.\s+(.*)', string):
        items.append(match.strip())
    for match in re.findall(r'[-•]+\s+(.*)', string):
        items.append(match.strip())
    return items 

def feedback_on_assembly(object, child_part, child_material, parent_part, parent_material,n=3):
    recommendation_prompt = f'''
        What can be used to attach a {object} {child_part} made of {child_material} to a {object} {parent_part} made of {parent_material}? 
        Give {n} recommendations. For each recommendation, give your reason. Separate the recommendation and reason by a | . Return in bullet points.
    '''

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=recommendation_prompt,
        max_tokens=512,
        temperature=0.7,
    )

    items = parse_into_list(response["choices"][0]["text"])

    attachments = []
    for item in items:
        name = item.split("|")[0].strip()
        reason = item.split("|")[1].strip()
        keywords = extract_keywords(reason)
        attachments.append({"name":name,"reason":reason, "keywords":keywords})


    return attachments

def extract_keywords(text):
    return kw_extractor.extract_keywords(text)

def suggest_materials_by_style2(style,material_type,n_materials=5,object=None,part=None):
    prompt=f'''
    What examples of {material_type} materials are of {style} interior design style?

    For each example, give your reason. Separate the example and reason by a | . Return in bullet points.
    '''

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=512,
        temperature=0.7,
    )

    items = parse_into_list(response["choices"][0]["text"])

    materials = []
    for item in items:
        name = item.split("|")[0].strip()
        reason = item.split("|")[1].strip()
        keywords = extract_keywords(reason)
        materials.append({"name":name,"reason":reason, "keywords":keywords})

    return materials


def suggest_color_by_style2(style,n_themes=5):
    # prompt=f'''
    # What are colors that are of {style} interior design style? Return {n_themes} hex color palettes and their palette names in bullet points.
    # Separate the palette name and color palette with a |. In each color palette, separate the hex colors with a , .
    # Don't say anything else apart from the color palettes and their names.
    # '''

    prompt=f'''
    What are colors that are of {style} interior design style? Return {n_themes} hex color themes.
    
    Don't say anything else apart from the hex codes and theme name. Return them as a dictionary.
    '''
    # Return as a dictionary.  

    # # Using GPT-3
    # response = openai.Completion.create(
    #     model="text-davinci-003",
    #     prompt=prompt,
    #     max_tokens=764,
    #     temperature=0.7,
    # )
    # response_msg = response["choices"][0]["text"]

    # Using ChatGPT
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"user", "content":prompt}],
    )
    response_msg = response["choices"][0]["message"]["content"]
    color_palettes = ast.literal_eval(response_msg)

    # items = parse_into_list(response_msg)

    # color_palettes = []
    # for item in items:
    #     name = item.split("|")[0].strip()
    #     palette_str = item.split("|")[1].strip()
    #     palette = palette_str.split(",")
    #     color_palettes.append({"name":name, "palette":palette})

    return color_palettes

def suggest_color_by_style(style,n_themes=5):
    prompt=f'''
    What are colors that are of {style} interior design style? Return {n_themes} hex color themes.
    
    Don't say anything else apart from the hex codes and theme name. Return them as a dictionary.
    '''

    # For now, we make pre-generated responses.
    match style.lower():
        case 'traditional':
            color_palettes = {
                "Warm Neutrals": ["#8B6E4B", "#CDB7A5", "#FFF8E7", "#EFE6D0", "#E9D6B8"],
                "Soft Blues and Greens": ["#85A3B2", "#E3DCC3", "#3B514C", "#8AA0A9", "#B1C1C0"],
                "Rich Reds and Golds": ["#824B4B", "#E6CCB2", "#B37A57", "#C88C53", "#E8B188"],
                "Deep Greens and Blues": ["#4C4E5A", "#7F9EB2", "#C5D0E6", "#67888F", "#B9D1C9"],
                "Creams and Beiges": ["#F5F5DC", "#E1D1B2", "#DBD5C4", "#C5B9A5", "#F5F5F5"]
            }
            return color_palettes
        case 'modern':
            color_palettes = {
                "Black and White": ["#000000", "#FFFFFF"],
                "Cool Grays": ["#A3A3A3", "#808080", "#545454"],
                "Neutral Earth Tones": ["#C5B596", "#D5C5A5", "#E5D5B5", "#F5E5C5"],
                "Bold Accents": ["#EF5B5B", "#EFC95F", "#71B8AF", "#5B5B5B"],
                "Soft Pastels": ["#AEB3CB", "#D9A5A5", "#C5D9D9", "#C5D9AF"]
            }
            return color_palettes
        case 'contemporary':
            color_palettes = {
                "Cool Monochromes": ["#4D4D4D", "#919191", "#D9D9D9", "#FFFFFF"],
                "Bold Neutrals": ["#333333", "#666666", "#CCCCCC", "#F5F5F5"],
                "Vibrant Accents": ["#FF5733", "#5E5E5E", "#F2F2F2", "#333333"],
                "Metallics": ["#C7C7C7", "#F0F0F0", "#FFC107", "#212121"],
                "Nature-Inspired": ["#BFAC8B", "#C2D2AF", "#4A4A4A", "#E6E6E6"]
            }
            return color_palettes
        case 'industrial':
            color_palettes = {
                "Rustic Neutrals": ["#8C756A", "#9E9E9E", "#CFCFCF", "#F5F5F5"],
                "Earthy Tones": ["#D9C9A7", "#A67C52", "#4A4A4A", "#E6E6E6"],
                "Blue and Gray": ["#7B8D8E", "#BFBFBF", "#E1E1E1", "#FFFFFF"],
                "Monochrome": ["#4A4A4A", "#7B7B7B", "#C1C1C1", "#F5F5F5"],
                "Metallic Accents": ["#484848", "#D1D1D1", "#F2F2F2", "#BFBFBF"]
            }
            return color_palettes
        case 'transitional':
            color_palettes = {
                "Timeless Neutrals": ["#E8E8E8", "#DCDCDC", "#BFBFBF", "#808080", "#000000"],
                "Soothing Blues": ["#BFD8E0", "#97BDCF", "#87AEBF", "#678F9E", "#536C7B"],
                "Earthy Tones": ["#C9A67E", "#B87A58", "#A2613D", "#8E5430", "#6E3C24"],
                "Gentle Greys": ["#E8E8E8", "#DCDCDC", "#BFBFBF", "#808080", "#000000"],
                "Sophisticated Browns": ["#8E5430", "#6E3C24", "#5B3024", "#4F2613", "#3D1E0C"]
            }
            return color_palettes
        case 'rustic':
            color_palettes = {
                "Neutral Woods": ["#8E743D", "#BDA487", "#D5C6AA", "#F7F1DF"],
                "Earthy Tones": ["#A67C52", "#D9C9A7", "#736357", "#E6E6E6"],
                "Forest Colors": ["#694D3A", "#8B6B4B", "#A3A04E", "#D0D29B"],
                "Rustic Reds": ["#834E4D", "#B25B5B", "#C6AA97", "#F2E6DD"],
                "Cabin Colors": ["#564334", "#AB6E67", "#C5A687", "#F6F5DD"]
            }
            return color_palettes
        case 'bohemian':
            color_palettes = {
                "Jewel Tones": ["#732C7B", "#BFDBE2", "#9D9E92", "#B2B09B"],
                "Earthy Hues": ["#8C6954", "#E1AFAF", "#D6C8B6", "#D6B08A"],
                "Bright and Bold": ["#FF6138", "#FFFF9D", "#BEEB9F", "#79BD8F"],
                "Pastel Paradise": ["#BF5FFF", "#EFD3D7", "#D3F5F7", "#A4F4F9"],
                "Global Textiles": ["#4E4D4A", "#9B8D72", "#A69E80", "#C7B49B"]
            }
            return color_palettes
        case 'minimalist':
            color_palettes = {
                'Pure White': ['#FFFFFF'],
                'Black and White': ['#000000', '#FFFFFF'],
                'Earthy Neutrals': ['#D4C5A5', '#E0C8A8', '#C5B298', '#B2A58D', '#9C8E7D'],
                'Soft Pastels': ['#E8B8A7', '#D7D7B1', '#9CD9C6', '#89A7C0', '#C39BCA'],
                'Cool Grays': ['#E3E3E3', '#C8C8C8', '#AFAFAF', '#969696', '#7F7F7F']
            }
            return color_palettes
        case 'hollywood Regency':
            color_palettes = {
                "Bold and Beautiful": ["#ec0066", "#a30070", "#f38d68", "#2f2f2f", "#f1dcd5"],
                "Metallic Accents": ["#000000", "#ffffff", "#d4af37", "#bfbfbf", "#f6e7d2"],
                "Golden Era": ["#444444", "#dddddd", "#bfae76", "#8b3a3a", "#cfc5a6"],
                "Luxurious Neutrals": ["#000000", "#ffffff", "#8b8680", "#e6dbc4", "#cc9575"],
                "Classic Glamour": ["#000000", "#ffffff", "#8b3a3a", "#cc9575", "#e6dbc4"]
            }
            return color_palettes
        case 'scandinavian':
            color_palettes = {
                "Light and Airy": ["#732C7B", "#BFDBE2", "#9D9E92", "#B2B09B"],
                "Cool and Calm": ["#8C6954", "#E1AFAF", "#D6C8B6", "#D6B08A"],
                "Earthy Neutrals": ["#FF6138", "#FFFF9D", "#BEEB9F", "#79BD8F"],
                "Warm and Cozy": ["#BF5FFF", "#EFD3D7", "#D3F5F7", "#A4F4F9"],
                "Blue and Grey": ["#4E4D4A", "#9B8D72", "#A69E80", "#C7B49B"]
            }
            return color_palettes
        

    return 
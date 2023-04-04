
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

def suggest_materials_by_style(style,material_type,n_materials=5,object=None,part=None):
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


def suggest_color_by_style(style,n_themes=5):
    prompt=f'''
    What are colors that are of {style} interior design style? Return {n_themes} hex color themes.
    
    Don't say anything else apart from the hex codes and theme name. Return them as a dictionary.
    '''

    # Using ChatGPT
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"user", "content":prompt}],
    )
    response_msg = response["choices"][0]["message"]["content"]
    color_palettes = ast.literal_eval(response_msg)

    return color_palettes


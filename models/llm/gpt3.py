
import os 
import openai
openai.api_key=os.getenv("OPENAI_API_KEY") #If first time using this repo, set the environment variable "OPENAI_API_KEY", to your API key from OPENAI
import re , ast
import yake 

kw_extractor = yake.KeywordExtractor(lan='en',n=3,top=20,dedupLim=0.9)


system_prompt = '''
    I want you to act as an interior and furniture design expert with expert knowledge of materials. Your role is to:

    1) Suggest materials and color palettes when asked, depending on the criteria to suggest them.
    2) Provide feedback on materials when asked, depending on the criteria to provide feedback.

    Now, introduce yourself to the user.
'''

n_material_suggestion_prompts=3
materials_suggestion_prompt = f'''
    Brainstorm prompts that the user can ask you to suggest materials. 
    Make sure that these prompts of suggesting materials are based on criteria to suggest materials such as 
    price (relatively expensive, relatively low-cost), a specific interior design style (e.g. Scandinavian, Contemporary), 
    environmental sustainability, durability, setting (e.g. outdoor, indoor, coastal, tropical), local availability in a certain city, state, or province etc.
    Make the prompts concise.
    Return {n_material_suggestion_prompts} prompts.
'''

message_history = []
temperature=0.0
init_history = [{"role":"system", "content":system_prompt}]

def get_message_history():
    return message_history


def parse_into_list(string):
    items = []
    for match in re.findall(r'\d+\.\s+(.*)', string):
        items.append(match.strip())
    for match in re.findall(r'[-•]+\s+(.*)', string):
        items.append(match.strip())
    return items 

def init_query():
    response = query(system_prompt,"system")
    return response

def query(prompt,role="user"):
    global message_history
    message_history.append({"role":role, "content":prompt})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=message_history,
        temperature=temperature
    )

    response_msg = response["choices"][0]["message"]["content"]
    message_history.append({"role":response["choices"][0]["message"]["role"], "content":response_msg})

    return response_msg

def suggest_materials(prompt,role="user"):
    refined_prompt = f"{prompt}"
    initial_response = query(refined_prompt,role)

    intro_text = initial_response.split('\n')[0].strip()

    python_dict_prompt= "Now, return the suggested materials and their reasons as a Python dictionary. Do not say anything else apart from the dictionary."
    python_dict_response = query(python_dict_prompt,role)

    suggestions = ast.literal_eval(python_dict_response)

    return intro_text, suggestions



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

    # Using ChatGPT
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"user", "content":prompt}],
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


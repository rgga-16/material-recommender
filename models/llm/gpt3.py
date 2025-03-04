
import copy
import openai, tiktoken
from openai import OpenAI
 #If first time using this repo, set the environment variable "OPENAI_API_KEY", to your API key from OPENAI
import re , ast, json, time
from datetime import datetime
from langchain_community.tools import DuckDuckGoSearchResults
from pydantic import BaseModel 
from typing import List

client = OpenAI()

def remove_https(s):
    return s.replace('https://', '')

def remove_after_paren(s):
    # Use regex to remove the string in specified format
    return  re.sub("\(.*\.\.\.,", ",", s)

def remove_non_ascii(s):
    return ''.join(i if ord(i) < 128 else ' ' for i in s)

def correct_string(input_string):
    # Replace specific string patterns
    input_string = input_string.replace("[snippet:", "{\"snippet\":\"")
    input_string = input_string.replace(", title:", ", \"title\":\"")
    input_string = input_string.replace(", link:", ", \"link\":\"")
    input_string = input_string.replace("],", "\"},")
    input_string = input_string.replace("]", "\"}")
    input_string = input_string.replace("[", "{")
    
    # Add quotes around the values
    # input_string = ': "'.join(input_string.split(":"))
    # input_string = '",'.join(input_string.split(","))
    
    # Return the corrected string only
    return "[" + input_string + "]"

def string_to_dict(s): 

    # Split the string by "], [" to get the individual items
    items = re.split(r'\], \[', s)

    # For each item, replace the leading and trailing brackets
    items = [re.sub(r'^\[', '', re.sub(r'\]$', '', item)) for item in items]

    # For each item, split by ', '. We end up with a list of lists.
    items = [re.split(r', ', item) for item in items]

    # For each item, split by ': '. We end up with a list of lists of lists.
    items = [[re.split(r': ', field, 1) for field in item] for item in items]

    # Parse the list of lists of lists into a list of dictionaries
    list_of_dicts = []
    for i in range(len(items)):
        item_list=items[i]
        dictionary ={"snippet":"", "title":"", "link":""}
        for k in range(len(item_list)):
            item = item_list[k]
            if(len(item)>1):
                if(item[0]=="snippet"):
                    snippet_value = item[1]
                    for j in range(k,len(item_list)):
                        item2 = item_list[j]
                        if(len(item2)<2):
                            snippet_value+=item2[0]
                    dictionary["snippet"] = snippet_value
                elif(item[0]=="title"):
                    dictionary["title"] = item[1]
                elif(item[0]=="link"):
                    dictionary["link"] = item[1]
        list_of_dicts.append(dictionary)

    return list_of_dicts


system_prompt = '''
I want you to act as an interior and furniture design expert with expert knowledge of materials. Your role is to:

1) Suggest materials and color palettes when asked, depending on the criteria to suggest them.
2) Provide feedback on materials when asked, depending on the criteria to provide feedback.

Now, introduce yourself to the user.
'''

n_material_suggestion_prompts=5
materials_suggestion_prompt = f'''
Brainstorm prompts that the user can ask you to suggest materials. 
Make sure that these prompts of suggesting materials are based on criteria to suggest materials such as 
price (relatively expensive, relatively low-cost), a specific interior design style (e.g. Scandinavian, Contemporary), 
environmental sustainability, durability, setting (e.g. outdoor, indoor, coastal, tropical), local availability in a certain city, state, or province etc.
Make the prompts concise.
Return {n_material_suggestion_prompts} prompts.
'''

texture_map_keywords_prompt_with_3d_model_context= '''
I am using DALL-E to create an image texture map of bamboo by typing in a textual description. I intend to use this texture map for a 3D model of a basket.

Brainstorm example keywords or key phrases I can append to the textual description that can satisfy both of the following conditions:

1) Make a detailed and more accurate image texture map of bamboo material. 
2) The texture map is visually appropriate to use for a 3D model of a basket.

I want you to return the keywords only as a Python list. Do not say anything else apart from the Python list.
'''


message_history = []
temperature=1.0
# model_name = "gpt-3.5-turbo"
# max_tokens = 4097
# model_name = "gpt-3.5-turbo-16k"

# model_name= "gpt-4"
# max_tokens=16383

# model_name = "gpt-4-1106-preview"
model_name = "gpt-4o"
max_tokens=100000
# max_tokens = 8096
encoding = tiktoken.get_encoding("cl100k_base")
# encoding = tiktoken.encoding_for_model(model_name)

init_history = [{"role":"system", "content":system_prompt[:system_prompt.index("Now, introduce yourself to the user.")]}]

# Code borrowed from https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo" or model=="gpt-3.5-turbo-16k":
        print("Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301")
    elif model == "gpt-4":
        print("Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0314.")
        return num_tokens_from_messages(messages, model="gpt-4-0314")
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif model == "gpt-4-0314" or model == "gpt-4o":
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError(f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens

def check_and_trim_message_history():
    offset=300
    global message_history
    global max_tokens
    global model_name 

    model_name_ = model_name
    if(model_name=="gpt-4-1106-preview" or model_name=="gpt-4o"):
        model_name_="gpt-4"

    if num_tokens_from_messages(message_history, model=model_name_) > max_tokens:
        print("Current number of tokens in message history exceeds the maximum number of tokens allowed. Trimming message history.")
        while num_tokens_from_messages(message_history, model=model_name_) > max_tokens - offset:
            del message_history[1] # Delete the 2nd message in the history. The first message is always the system prompt, which should not be deleted.
            

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


def internet_search(query,role="user",n_results=10):
    global message_history 
    search = DuckDuckGoSearchResults(num_results=n_results)
    results=[]
    prompt = f'''
        Disregard any previous instructions.
        I will give you a question or an instruction. Your objective is to answer my question or fulfill my instruction.
        My question or instruction is: {query}
        For your reference, today's date is {datetime.now().isoformat()}.
        It's possible that the question or instruction, or just a portion of it, requires relevant information from the internet to give a satisfactory answer or complete the task. 
        Therefore, provided below is the necessary information obtained from the internet, which sets the context for addressing the question or fulfilling the instruction. 
        You will write a comprehensive reply to the given question or instruction. 
        Make sure to cite results using [[NUMBER](URL)] notation after the reference. 
        If the provided information from the internet results refers to multiple subjects with the same name, write separate answers for each subject:
    '''
    results_str= search.run(query)
    results_str = results_str.replace('\u2026', '...')
    results = ast.literal_eval(results_str)
    for i in range(len(results)):
        r = results[i]
        prompt += f'''\n
            NUMBER:{i+1}
            URL:{r['link']}
            TITLE:{r['title']}
            CONTENT:{r['snippet']}
        '''
    return prompt, results 

def translate(text,target_lang, source_lang,role="user"):

    system_prompt = '''
        Act as a translator between Japanese and English. 
        Whenever you are given a text, please translate it to the opposite language. 
        Make sure you use polite and formal language, and make sure the terms you will use is relevant to the context presented in the text.
    '''
    # prompt=text
    prompt = f'''
        Translate the following text below from {source_lang} to {target_lang}. If it is already in {target_lang}, then do not translate it and keep the original text. Do not say anything else apart from the translated text.

        {text}
    '''
    history = [{"role":"system", "content":system_prompt}]
    history.append({"role":role, "content":prompt})
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=history,
            temperature=0.1
        )
        response_msg = response.choices[0].message.content
    except Exception as e:
        response_msg = f"Translation Error"

    return response_msg

def query(prompt,role="user", temp=temperature):
    global message_history
    message_history.append({"role":role, "content":prompt})
    check_and_trim_message_history()

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=message_history,
            temperature=temp
        )
        response_msg = response.choices[0].message.content
        message_history.append({"role":response.choices[0].message.role, "content":response_msg})
    except Exception as e:
        response_msg = f"Error: {e}"
    return response_msg

def suggest_finish_settings(finish_name, material_name, object_name, part_name, role="user"):
    if(object_name==part_name):
        object_str = f"The 3D object you are applying the finish onto is a {object_name}."
    else:
        object_str = f"The 3D object is a {object_name} and the part of the object you are applying the finish onto is the {part_name}."

    prompt=f'''
    Imagine you are putting settings for a finish you want to add onto the material for a 3D object in a 3D modelling software.
    {object_str} 
    The material you want to add the finish to is the {material_name}.
    Here are the following settings you can edit, their range of values for the finish, and a description of each setting:
    - Roughness: 0.0 to 1.0. This controls the shine of the material. Values less than 0.5 would give a smoother and glossier finish while a greater than 0.5 would give a rougher and more matte finish.
    - Metallic: 0.0 to 1.0. This controls the metallicness of the material. Values less than 0.5 would make the material look less metallic while a greater than 0.5 would make the material look more metallic.
    - Opacity: 0.0 to 1.0. This controls the opacity of the material. Values less than 0.5 would make the material more transparent while a greater than 0.5 would make the material more opaque.
    Now, return the suggested setting values for the finish, {finish_name}, as a Python dictionary.
    The keys should be the setting names, and the values should be the suggested setting values.
    '''
    # Do not say anything else apart from the Python dictionary.
    global init_history
    init_history_clone = copy.deepcopy(init_history)
    init_history_clone.append({"role":"user", "content":prompt})
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=init_history_clone,
        temperature=0.2
    )
    suggested_settings_str = response.choices[0].message.content

    # Remove text before and after the Python dict
    start_index = suggested_settings_str.find('{')
    if start_index>0:
        print("Removing text before the Python dictionary.")
        suggested_settings_str = suggested_settings_str[start_index:].strip()
    end_index = suggested_settings_str.rfind('}')
    if end_index<len(suggested_settings_str)-1:
        print("Removing text after the Python dictionary.")
        suggested_settings_str = suggested_settings_str[:end_index+1].strip()
    suggested_settings_str = suggested_settings_str.strip()

    try:
        suggested_settings = ast.literal_eval(suggested_settings_str)
    except SyntaxError as e:
        suggested_settings = {
            "roughness": 0.5,
            "metallic": 0.5,
            "opacity": 0.5
        }
        print(f"Sorry, please try again. We got the following error: {e}.")

    for key in list(suggested_settings.keys()):
        new_key = key.strip().lower()
        suggested_settings[new_key] = suggested_settings.pop(key)

    return suggested_settings

def suggest_materials_2(prompt,role="user", use_internet=True, design_brief=None,n=5):
    start_time= time.time()
    refined_prompt = f"{prompt}"
    if use_internet:
        refined_prompt,_ = internet_search(refined_prompt,role)

    if design_brief:
        refined_prompt+= f''' 
        Additionally, I want you to consider the following design brief for context: 
        ==========================
        {design_brief}.
        ==========================
        Some parts of the design brief may be relevant to the question or instruction, while others may not be relevant.
        '''

        if use_internet:
            refined_prompt+= '''
            You may refer to the aforementioned sources retrieved from the internet in the previous message.
            Make sure to cite results using [[NUMBER](URL)] notation after the reference.
            Make sure that you answer the question or fulfill the instruction by both using the sources from the internet and also in the context of the design brief.
            '''
        else: 
            refined_prompt+=  '''
            Make sure that you answer the question or fulfill the instruction in the context of the design brief.
            '''
    
    if use_internet: 
        refined_prompt+= f'''Lastly, answer the suggested materials and their detailed reasons as a Python dictionary. 
        The keys are the names of the suggested materials, and the values are the detailed reasons. The detailed reasons should be written using Markdown.
        Make sure the reasons are the same as the ones in the previous response, and maintain their reference citations.'''
    else: 
        refined_prompt+= '''
        Lastly, answer the suggested materials and their detailed reasons as a Python dictionary. 
        The keys are the names of the suggested materials, and the values are the detailed reasons. The detailed reasons should be written using Markdown.
        Make sure the reasons are the same as the ones in the previous response.'''
        

    dict_template = {
        "material 1": "Reason 1",
        "material 2": "Reason 2",
        "material 3": "Reason 3",
        "material 4": "Reason 4",
    }
    dict_template_str = json.dumps(dict_template, indent=4)

    refined_prompt+=f"Here is an example of the said Python dictionary: {dict_template_str}"

    refined_prompt+= '''Do not respond anything else apart from the dictionary.
    Do not respond anything else apart from the dictionary.
    Do not respond anything else apart from the dictionary.'''

    python_dict_response_str = query(refined_prompt,role).strip()
    end_time = time.time()
    print(f"Time elapsed: {end_time-start_time} seconds.")

    # Remove text before and after the Python list
    start_index = python_dict_response_str.find('{')
    if start_index>0:
        print("Removing text before the Python list.")
        python_dict_response_str = python_dict_response_str[start_index:].strip()
    end_index = python_dict_response_str.rfind('}')
    if end_index<len(python_dict_response_str)-1:
        print("Removing text after the Python list.")
        python_dict_response_str = python_dict_response_str[:end_index+1].strip()

    python_dict_response_str = python_dict_response_str.strip()

    try:
        suggestions = ast.literal_eval(python_dict_response_str)
        intro_text=''
    except SyntaxError as e:
        intro_text = f"Sorry, please try again. We got the following error: {e}."
        global message_history
        message_history=message_history[:-2]
        suggestions = {}
    return intro_text, suggestions

def suggest_materials_3(prompt,role="user", resources="", design_brief=None,n=5):
    refined_prompt = f"{prompt}"

    if design_brief:
        refined_prompt+= f''' 
        Additionally, I want you to consider the following design brief for context: 
        ==========================
        {design_brief}.
        ==========================
        Some parts of the design brief may be relevant to the question or instruction, while others may not be relevant.
        '''

        if resources not in ["", None]:
            # refined_prompt+= '''
            # Also, provided here are excerpts from textbook sources that could be relevant to the query. 
            # If you will use these excerpts, not only should you cite their page number and textbook title, but please do not give the full answer to the question or instruction. 
            # Instead, give a small part of the answer, and then encourage the user to refer to the cited textbooks and their page numbers for the full answer. 
            # The point of providing these excerpts is to educate the user and help them improve their knowledge.
            # Make sure that you answer the question or fulfill the instruction by both using these excerpts from textbooks and also in the context of the design brief.
            # '''
            refined_prompt+= '''
            Also, provided here are excerpts from textbook sources that could be relevant to the query. 
            If you will use these excerpts, not only should you cite their page number and textbook title, but please do not give the answer to the question or instruction. 
            Instead, then encourage the user to refer to the cited textbooks and their page numbers for the full answer. 
            The point of providing these excerpts is to educate the user and help them improve their knowledge.
            '''
        else: 
            refined_prompt+=  '''
            Make sure that you answer the question or fulfill the instruction in the context of the design brief.
            '''
    
    if resources not in ["", None]: 
        refined_prompt+= f'''Lastly, answer the suggested materials and their detailed reasons as a Python dictionary. 
        The keys are the names of the suggested materials, and the values are the detailed reasons. 
        The detailed reasons should be written using Markdown AND should not tell the answer but encourage the user to refer to the cited textbooks and their page numbers for the full answer.
        Make sure the reasons are the same as the ones in the previous response.'''
    else: 
        refined_prompt+= '''
        Lastly, answer the suggested materials and their detailed reasons as a Python dictionary. 
        The keys are the names of the suggested materials, and the values are the detailed reasons. The detailed reasons should be written using Markdown.
        Make sure the reasons are the same as the ones in the previous response.'''
        

    dict_template = {
        "material 1": "Reason 1",
        "material 2": "Reason 2",
        "material 3": "Reason 3",
        "material 4": "Reason 4",
    }
    dict_template_str = json.dumps(dict_template, indent=4)

    refined_prompt+=f"Here is an example of the said Python dictionary: {dict_template_str}"

    refined_prompt+= '''Do not respond anything else apart from the dictionary.
    Do not respond anything else apart from the dictionary.
    Do not respond anything else apart from the dictionary.'''

    python_dict_response_str = query(refined_prompt,role).strip()
    end_time = time.time()

    # Remove text before and after the Python list
    start_index = python_dict_response_str.find('{')
    if start_index>0:
        print("Removing text before the Python list.")
        python_dict_response_str = python_dict_response_str[start_index:].strip()
    end_index = python_dict_response_str.rfind('}')
    if end_index<len(python_dict_response_str)-1:
        print("Removing text after the Python list.")
        python_dict_response_str = python_dict_response_str[:end_index+1].strip()

    python_dict_response_str = python_dict_response_str.strip()

    try:
        suggestions = ast.literal_eval(python_dict_response_str)
        intro_text=''
    except SyntaxError as e:
        intro_text = f"Sorry, please try again. We got the following error: {e}."
        global message_history
        message_history=message_history[:-2]
        suggestions = {}
    return intro_text, suggestions


class ColorPalette(BaseModel):
    name: str
    description: str
    codes: List[str]

class ColorPalettes(BaseModel):
    color_palettes: List[ColorPalette]

def suggest_color_palettes(prompt, role="user", use_internet=True, design_brief=None):
    refined_prompt = f"{prompt}. Suggest color palettes."
    if use_internet:
        refined_prompt,_ = internet_search(refined_prompt,role)
    
    if design_brief:
        refined_prompt+= f''' 
        Additionally, I want you to consider the following design brief for context: 
        ==========================
        {design_brief}.
        ==========================
        Some parts of the design brief may be relevant to the question or instruction, while others may not be relevant.
        '''

        if use_internet:
            refined_prompt+= '''
            You may refer to the aforementioned sources retrieved from the internet in the previous message.
            Make sure to cite results using [[NUMBER](URL)] notation after the reference.
            Make sure that you answer the question or fulfill the instruction by both using the sources from the internet and also in the context of the design brief.
            '''
        else: 
            refined_prompt+=  '''
            Make sure that you answer the question or fulfill the instruction in the context of the design brief.
            '''
    
    if use_internet:
        refined_prompt+='''
        Now, return the suggested color palettes that contain hex color codes, their names, and their detailed descriptions from the previous response as a Python list of dictionaries. 
        Each dictionary should contain the following keys: name, description, codes. 
        The value of the names key should be a string.
        The value of the descriptions key should be a string.
        The value of the codes key should be a Python list of hex color codes.
        Make sure the descriptions are the same as the ones in the previous response, and maintain their reference citations.
        Do not say anything else apart from the Python list.
        '''
    else:
        refined_prompt+='''
        Now, return the suggested color palettes that contain hex color codes, their names, and their detailed descriptions from the previous response as a Python list of dictionaries. 
        Each dictionary should contain the following keys: name, description, codes. 
        The value of the names key should be a string.
        The value of the descriptions key should be a string.
        The value of the codes key should be a Python list of hex color codes.
        Make sure the descriptions are the same as the ones in the previous response.
        Do not say anything else apart from the Python list.
        '''
    
    refined_prompt = refined_prompt.strip()
    
    example = [
        {
            "name": "Bright and Bold",
            "description": "This color palette is inspired by the colors of the sky during sunset. The colors are warm and vibrant.",
            "codes": ["#FFC300", "#FF5733", "#C70039", "#900C3F", "#581845"]
        }
    ]
    refined_prompt+=f"Here is an example of the said Python list: {example}"

    global message_history
    message_history.append({"role":role, "content":refined_prompt})

    response=client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=message_history,
        response_format=ColorPalettes
    )

    color_palettes = response.choices[0].message.parsed.color_palettes
    formatted_color_palettes = []
    for cp in color_palettes:
        formatted_color_palettes.append({
            "name": cp.name,
            "description": cp.description,
            "codes": cp.codes
        })

    intro_text=''
    return intro_text, formatted_color_palettes

    # python_list_response = query(refined_prompt,role).strip()
    # orig_python_list_response = copy.deepcopy(python_list_response)
    # intro_text = ""

    # # Remove text before and after the Python list
    # start_index = python_list_response.find('[{')
    # if start_index>0:
    #     print("Removing text before the Python list.")
    #     python_list_response = python_list_response[start_index:].strip()
    
    # end_index = python_list_response.rfind('}]')
    # if end_index<len(python_list_response)-2:
    #     print("Removing text after the Python list.")
    #     python_list_response = python_list_response[:end_index+2].strip()
    # python_list_response = python_list_response.strip()

    
    # try:
    #     suggestions = ast.literal_eval(python_list_response)
    #     # intro_text=''
    # except SyntaxError as e:
    #     intro_text = f"Sorry, please try again. We got the following error: {e}."
    #     global message_history
    #     message_history=message_history[:-2]
    #     suggestions = []
    
    # return intro_text, suggestions


class TextureMapKeywords(BaseModel):
    keywords: List[str]


def brainstorm_prompt_keywords(material, design_brief=None):

    
    texture_map_keywords_prompt = f'''
        I am using DALL-E 3 to create an image of a {material} texture map by typing in a text prompt.
        Brainstorm example keywords I can append to the textual description to make a detailed and more accurate image of a {material} texture map.
    '''
    if design_brief: 
        texture_map_keywords_prompt = f'''
            I am using DALL-E 3 to create an image of a {material} texture map by typing in a text prompt.
            I'm trying to make a texture map that best aligns with the contents of the following design brief:
            ==========================
            {design_brief}
            ==========================
            Based on these priors, this is my instruction: Brainstorm example keywords I can append to the text prompt to make a detailed and more accurate image of a {material} texture map. 
        '''

    global init_history
    init_history_clone = copy.deepcopy(init_history)
    init_history_clone.append({"role":"user", "content":texture_map_keywords_prompt})

    response=client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=init_history_clone,
        response_format=TextureMapKeywords
    )

    keywords = response.choices[0].message.parsed.keywords
    return keywords

def brainstorm_material_queries(): 
    global init_history
    init_history_clone = copy.deepcopy(init_history)
    init_history_clone.append({"role":"user", "content":materials_suggestion_prompt})

    initial_response = client.chat.completions.create(
        model=model_name,
        messages=init_history_clone,
        temperature=1.0
    )
    
    init_history_clone.append({"role":"assistant", "content":initial_response.choices[0].message.content})
    python_list_prompt = "Now, return the brainstormed prompts as a Python list. Do not say anything else apart from the list."
    init_history_clone.append({"role":"user", "content":python_list_prompt})

    python_list_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=init_history_clone,
        temperature=0.0
    )

    try: 
        prompts = ast.literal_eval(python_list_response.choices[0].message.content)
    except SyntaxError as e:
        prompts = ["(Error. Please try again.)"]
        print(f"Sorry, please try again. We got the following error: {e}.")

    return prompts

class GeneratedFeedback(BaseModel):
    aspect: str
    feedback: str
    suggestions: List[List[str]]


materials_feedbacks = []
def provide_material_feedback2(material_name, object_name, part_name, use_internet=False, attached_parts=None, design_brief=None):
    # feedback_model = "gpt-3.5-turbo-16k"
    feedback_model = "gpt-4"
    aspects = ["durability", "maintenance", "sustainability", "assembly", "cost", "availability"]
    if(object_name==part_name):
        part_name=""
    material_feedback_prompt_head = f"I have a {object_name} {part_name} made out of {material_name}. "
    
    materials_parts=""
    if attached_parts is not None and len(attached_parts)>0:
        materials_parts = f'''Here is information on other parts it is attached to : \n'''
        for attached_part in attached_parts:
            parent = attached_part[0]
            part=attached_part[1]
            if parent==part:
                materials_parts += f'''It is attached to a {attached_part[0]} made out of {attached_part[2]}. '''
            else:
                materials_parts += f'''It is attached to a {attached_part[0]} {attached_part[1]} made out of {attached_part[2]}. '''
    

    material_feedback_task = f'''\nBased on the provided information above, your task is to provide feedback on the material used based on the following aspects: {", ".join(aspects[:-1])} {", and " + aspects[-1]}. 
    For each aspect, if you gave critical feedback on that aspect, please provide up to 5 suggestions 
    (e.g. alternative materials, adding material finishes, assembly attachments) to improve the aspect. 
    Make sure that you also consider the object that the material is used on.
    '''
    
    materials_internet_sources = ""
    references=[]
    if use_internet:
        results = []
        materials_internet_sources += f'''\n 
        Additionally, here are sources from the internet that you can refer to and cite when providing feedback: \n
        '''
        src_idx=1
        for i in range(len(aspects)):
            aspect = aspects[i]
            internet_search_query = f'{aspect} of a {object_name} {part_name} made out of {material_name}'
            _, results = internet_search(internet_search_query,role="user",n_results=3)
            materials_internet_sources += f"**{aspect}**:"

            for r in results:
                materials_internet_sources += f'''\n
                NUMBER:{src_idx}
                URL:{r['link']}
                TITLE:{r['title']}
                CONTENT:{r['snippet']}
                '''
                references.append({
                    "number":src_idx,
                    "url":r['link'],
                    "title":r['title'],
                })
                src_idx+=1
        materials_internet_sources += f'''
        Make sure to cite results using [[NUMBER](URL)] notation after the reference. 
        If the provided information from the internet results refers to multiple subjects with the same name, write separate answers for each subject.
        '''
    
    design_brief_context = ""
    if design_brief:
        design_brief_context+= f''' 
        Additionally, I want you to consider the following design brief for context: 
        ==========================
        {design_brief}.
        ==========================
        Some parts of the design brief may be relevant to , while others may not be relevant.
        '''

        if use_internet:
            design_brief_context+= '''
            You may refer to the aforementioned sources retrieved from the internet.
            Make sure to cite results using [[NUMBER](URL)] notation after the reference.
            Make sure that you fulfill the task by both using the sources from the internet and also in the context of the design brief.
            '''
        else: 
            design_brief_context+=  '''
            Make sure that you fulfill the task in the context of the design brief.
            '''
    
    material_feedback_format = f'''Lastly, please provide your feedback in the form of a Python dictionary. 
    The keys should be the aspects: {", ".join(aspects[:-1])} {", and " + aspects[-1]}. The values of each aspect are "feedback" and "suggestions".
    "feedback" is the key to the feedback you provided for that aspect. Make sure that the feedback is in Markdown format and it is exactly the same as the feedback you provided for that aspect in the previous response.
    "suggestions" is a list of lists where each list contains the name of the suggested item and item type.
    The item type must either be one of the following: material, finish, attachment, or other.
    Here is a template:
    '''
    dict_template = {}
    for i in range(len(aspects)):
        aspect = aspects[i]
        dict_template[aspect] = {
            "feedback": f"{aspect} feedback",
            "suggestions": [["item1","item_type"], ["item2","item_type"]]
        }
    
    dict_template_str = json.dumps(dict_template, indent=4)
    material_feedback_format+=dict_template_str
    material_feedback_format+=f'''Do not respond anything else apart from the dictionary. Do not respond anything else apart from the dictionary. Do not respond anything else apart from the dictionary.
    '''

    material_feedback_prompt = material_feedback_prompt_head + materials_parts + material_feedback_task + materials_internet_sources + design_brief_context + material_feedback_format
    print(material_feedback_prompt)
    global init_history
    init_history_clone = copy.deepcopy(init_history)
    init_history_clone.append({"role":"user", "content":material_feedback_prompt})

    
    response = client.chat.completions.create(
        model=feedback_model,
        messages=init_history_clone,
        temperature=0.1
    )
    suggestions_dict_str = response.choices[0].message.content

    # Remove text before and after the Python dict
    start_index = suggestions_dict_str.find('{')
    if start_index>0:
        print("Removing text before the Python dictionary.")
        suggestions_dict_str = suggestions_dict_str[start_index:].strip()
    end_index = suggestions_dict_str.rfind('}')
    if end_index<len(suggestions_dict_str)-1:
        print("Removing text after the Python dictionary.")
        suggestions_dict_str = suggestions_dict_str[:end_index+1].strip()

    suggestions_dict_str = suggestions_dict_str.strip()

    try:
        suggestions_dict= ast.literal_eval(suggestions_dict_str)
    except SyntaxError as e:
        intro_text = f"Sorry, please try again. We got the following error: {e}."
        suggestions_dict = {}

    unformatted_response = ""
    intro_text = ""
    return intro_text, unformatted_response, suggestions_dict, references

class TexturePromptList(BaseModel):
    texture_prompts: List[str]
    reasons: List[str]

class MaterialSuggestionPromptList(BaseModel):
    suggested_materials: List[str]
    explanations: List[str]
    texture_prompts: List[str]


def suggest_materials_texturebased(material_name, prompt, n, texture_image, design_brief, interior_state=None):
    priors = "specified material" 
    
    background = f'''Here is the material, {material_name}. The attached image is its texture map for your reference.'''
    
    if design_brief not in ["", None]:
        background += f'''
        Additionally, here is a design brief for context on how the material may be used. It may be used on a 3D model of an element in the space.
        ==========================
        {design_brief}
        ==========================
        '''
        priors += " and contents of the design brief"
    
    if interior_state not in ["", None]:
        background += f''' 
            Moreover, there is another picture showing the current state of the interior space which includes a visual on the materials and colors being used. 
        '''
        priors += " and the current state of the interior space"

    instruction = f'''
        Based on the {priors}, please suggest {n} materials that are similar to {material_name} material and that also address the following query (if any, ignore if none): {prompt}. 
        If the material name is generic (e.g., wood, metal), you can suggest specific materials that are within the same category.
        Moreover, please also provide a short and concise explanation, as well as a detailed texture map prompt for each material. 
        If a design brief is included, please consider it when suggesting the similar materials and making the reasons.
        If there is a design brief included, don't explicitly include details about the design brief in the texture map prompts. 
        If there is a picture of the current state of the interior space included, please consider it in order to suggest materials and colors that would complement the current state of the interior space.
    '''

    full_prompt = f'''{background} 
    {instruction}
    '''
    global init_history

    init_history_clone = copy.deepcopy(init_history)

    message = {
        "role":"user",
        "content": [
            {"type": "text", "text": full_prompt},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{texture_image}"},
            }
        ]
    }

    if interior_state not in ["", None]:
        message["content"].append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{interior_state}"},
            }
        )

    init_history_clone.append(message)

    # Use messages
    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=init_history_clone,
        max_tokens=5000,
        response_format=MaterialSuggestionPromptList  # Use the Pydantic model as the response format
    )

    structured_response = response.choices[0].message.parsed

    return structured_response.suggested_materials, structured_response.explanations, structured_response.texture_prompts



def suggest_texture_prompts(prompt,n, image, design_brief=None, interior_state=None):
    priors = "image"
    
    background = f'''Attached is an image of a texture map.'''

    if design_brief not in ["", None]:
        background += f'''
        Additionally, here is a design brief for context on how the texture map may be used. It may be used on a 3D model of an element in the space.:
        ==========================
        {design_brief}
        ==========================
        '''
        priors += " and contents of the design brief"
    
    if interior_state not in ["", None]:
        background += f''' 
            Moreover, there is another picture showing the current state of the interior space which includes a visual on the materials and colors being used. 
        '''
        priors += " and the current state of the interior space"

    instruction = f'''
        Based on the {priors}, please make {n} varying prompts that can be inputted in a text-to-image generator to create detailed flat texture map images of the material in the image.
        If there is a design brief included, don't explicitly include details about the design brief in the texture map prompts. 
        If there is a picture of the current state of the interior space included, please consider it in order to suggest materials and colors that would complement the current state of the interior space.
    '''

    if prompt not in ["", None]:
        background += f'''
        Additionally, here is a prompt provided that gives instructions on how to formulate the prompts:
        {prompt}
        '''

        instruction = f'''
        Based on the {priors}, please make {n} varying texture map prompts that can be inputted in a text-to-image generator to create detailed flat texture map images of the material in the image.
        If there is a design brief included, don't explicitly include details about the design brief in the texture map prompts.
        Moreover, make sure that the texture map prompts are also based on the prompt provided above.
        If there is a picture of the current state of the interior space included, please consider it in order to suggest materials and colors that would complement the current state of the interior space.
        '''
    
    full_prompt = f'''{background} 
    {instruction}
    '''

    global init_history

    init_history_clone = copy.deepcopy(init_history)

    message = {
        "role":"user",
        "content": [
            {"type": "text", "text": full_prompt},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image}"},
            }
        ]
    }

    if interior_state not in ["", None]:
        message["content"].append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{interior_state}"},
            }
        )

    init_history_clone.append(message)

    # Use messages
    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=init_history_clone,
        max_tokens=5000,
        response_format=TexturePromptList  # Use the Pydantic model as the response format
    )

    structured_response = response.choices[0].message.parsed
    return structured_response.texture_prompts
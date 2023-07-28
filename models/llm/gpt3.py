
import os, copy
import openai, tiktoken
openai.api_key=os.getenv("OPENAI_API_KEY") #If first time using this repo, set the environment variable "OPENAI_API_KEY", to your API key from OPENAI
import re , ast, json, time
import yake 
from datetime import datetime


from langchain.tools import DuckDuckGoSearchResults


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
model_name = "gpt-3.5-turbo-16k"
# model_name= "gpt-4"
max_tokens=16383
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
    elif model == "gpt-4-0314":
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

    if num_tokens_from_messages(message_history, model=model_name) > max_tokens:
        print("Current number of tokens in message history exceeds the maximum number of tokens allowed. Trimming message history.")
        while num_tokens_from_messages(message_history, model=model_name) > max_tokens - offset:
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

def translate(text,role="user"):

    system_prompt = '''
        Act as a translator between Japanese and English. 
        Whenever you are given a text, please translate it to the opposite language. 
        Make sure you use polite and formal language, and make sure the terms you will use is relevant to the context presented in the text.
    '''
    history = [{"role":"system", "content":system_prompt}]
    history.append({"role":role, "content":text})
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=history,
            temperature=0.1
        )
        response_msg = response["choices"][0]["message"]["content"]
    except Exception as e:
        response_msg = f"Translation Error"

    return response_msg

def query(prompt,role="user", temp=temperature):
    global message_history
    message_history.append({"role":role, "content":prompt})
    check_and_trim_message_history()

    try:
        response = openai.ChatCompletion.create(
            model=model_name,
            messages=message_history,
            temperature=temp
        )
        response_msg = response["choices"][0]["message"]["content"]
        message_history.append({"role":response["choices"][0]["message"]["role"], "content":response_msg})
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
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=init_history_clone,
        temperature=0.2
    )
    suggested_settings_str = response["choices"][0]["message"]["content"]

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

    # initial_response = query(refined_prompt,role)
    # intro_text = initial_response.split('\n')[0].strip()

    python_list_response = query(refined_prompt,role).strip()
    orig_python_list_response = copy.deepcopy(python_list_response)
    intro_text = ""

    # Remove text before and after the Python list
    start_index = python_list_response.find('[{')
    if start_index>0:
        print("Removing text before the Python list.")
        python_list_response = python_list_response[start_index:].strip()
    
    end_index = python_list_response.rfind('}]')
    if end_index<len(python_list_response)-2:
        print("Removing text after the Python list.")
        python_list_response = python_list_response[:end_index+2].strip()
    python_list_response = python_list_response.strip()

    
    try:
        suggestions = ast.literal_eval(python_list_response)
        # intro_text=''
    except SyntaxError as e:
        intro_text = f"Sorry, please try again. We got the following error: {e}."
        global message_history
        message_history=message_history[:-2]
        suggestions = []
    
    return intro_text, suggestions

def brainstorm_prompt_keywords(material):
    texture_map_keywords_prompt = f'''
        I am using DALL-E to create an image of a {material} texture map by typing in a textual description.
        Brainstorm example keywords I can append to the textual description to make a detailed and more accurate image of a {material} texture map. 
        I want you to answer only as a Python list. I want you to answer only as a Python list. I want you to answer only as a Python list. 
        Do not say anything else apart from the Python list.
    '''
    global init_history
    init_history_clone = copy.deepcopy(init_history)
    init_history_clone.append({"role":"user", "content":texture_map_keywords_prompt})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=init_history_clone,
        temperature=0.8
    )

    try: 
        keywords = ast.literal_eval(response["choices"][0]["message"]["content"])
    except SyntaxError as e:
        keywords = [["Error. Please try again."]]
        print(f"Sorry, please try again. We got the following error: {e}.")


    return keywords

def brainstorm_material_queries(): 
    global init_history
    init_history_clone = copy.deepcopy(init_history)
    init_history_clone.append({"role":"user", "content":materials_suggestion_prompt})

    initial_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=init_history_clone,
        temperature=0.7
    )
    
    init_history_clone.append({"role":"assistant", "content":initial_response["choices"][0]["message"]["content"]})
    python_list_prompt = "Now, return the brainstormed prompts as a Python list. Do not say anything else apart from the list."
    init_history_clone.append({"role":"user", "content":python_list_prompt})

    python_list_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=init_history_clone,
        temperature=0.0
    )

    try: 
        prompts = ast.literal_eval(python_list_response["choices"][0]["message"]["content"])
    except SyntaxError as e:
        prompts = ["(Error. Please try again.)"]
        print(f"Sorry, please try again. We got the following error: {e}.")

    return prompts


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
    if use_internet:
        results = []
        materials_internet_sources += f'''\n 
        Additionally, here are sources from the internet that you can refer to and cite when providing feedback: \n
        '''
        src_idx=1
        references = []
        for i in range(len(aspects)):
            aspect = aspects[i]
            internet_search_query = f'{aspect} of a {object_name} {part_name} made out of {material_name}'
            _, results = internet_search(internet_search_query,role="user",n_results=5)
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

    global init_history
    init_history_clone = copy.deepcopy(init_history)
    init_history_clone.append({"role":"user", "content":material_feedback_prompt})

    
    response = openai.ChatCompletion.create(
        model=feedback_model,
        messages=init_history_clone,
        temperature=0.1
    )
    suggestions_dict_str = response["choices"][0]["message"]["content"]

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












# DUMP (OLD CODE)
# def feedback_on_assembly(object, child_part, child_material, parent_part, parent_material,n=3):
#     recommendation_prompt = f'''
#         What can be used to attach a {object} {child_part} made of {child_material} to a {object} {parent_part} made of {parent_material}? 
#         Give {n} recommendations. For each recommendation, give your reason. Separate the recommendation and reason by a | . Return in bullet points.
#     '''

#     response = openai.Completion.create(
#         model="text-davinci-003",
#         prompt=recommendation_prompt,
#         max_tokens=512,
#         temperature=0.7,
#     )

#     items = parse_into_list(response["choices"][0]["text"])

#     attachments = []
#     for item in items:
#         name = item.split("|")[0].strip()
#         reason = item.split("|")[1].strip()
#         keywords = extract_keywords(reason)
#         attachments.append({"name":name,"reason":reason, "keywords":keywords})

#     return attachments

# def extract_keywords(text):
#     return kw_extractor.extract_keywords(text)


# def suggest_materials_by_style(style,material_type,n_materials=5,object=None,part=None):
#     prompt=f'''
#     What examples of {material_type} materials are of {style} interior design style?
#     For each example, give your reason. Separate the example and reason by a | . Return in bullet points.
#     '''

#     # Using ChatGPT
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[{"role":"user", "content":prompt}],
#         max_tokens=512,
#         temperature=0.7,
#     )
#     items = parse_into_list(response["choices"][0]["text"])
#     materials = []
#     for item in items:
#         name = item.split("|")[0].strip()
#         reason = item.split("|")[1].strip()
#         keywords = extract_keywords(reason)
#         materials.append({"name":name,"reason":reason, "keywords":keywords})
#     return materials

# def suggest_color_by_style(style,n_themes=5):
#     prompt=f'''
#     What are colors that are of {style} interior design style? Return {n_themes} hex color themes.
    
#     Don't say anything else apart from the hex codes and theme name. Return them as a dictionary.
#     '''

#     # Using ChatGPT
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[{"role":"user", "content":prompt}],
#     )
#     response_msg = response["choices"][0]["message"]["content"]

#     color_palettes = ast.literal_eval(response_msg)

#     return color_palettes

# def suggest_materials(prompt,role="user", use_internet=True, design_brief=None):
#     start_time= time.time()
#     refined_prompt = f"{prompt}"
#     if use_internet:
#         refined_prompt,_ = internet_search(refined_prompt,role)
#     initial_response = query(refined_prompt,role)
#     intro_text = initial_response.split('\n')[0].strip()

#     if design_brief:
#         context_aware_prompt = f''' 
#         Now, I want you to answer again but consider the following design brief for context: 
#         ==========================
#         {design_brief}.
#         ==========================
#         Some parts of the design brief may be relevant to the question or instruction, while others may not be relevant.
#         '''

#         if use_internet:
#             context_aware_prompt += '''
#             You may refer to the sources retrieved from the internet in the previous message.
#             Make sure to cite results using [[NUMBER](URL)] notation after the reference.
#             Make sure that you answer the question or fulfill the instruction by both using the sources from the internet and also in the context of the design brief.
#             '''
#         else: 
#             context_aware_prompt += '''
#             Make sure that you answer the question or fulfill the instruction in the context of the design brief.
#             '''
#         context_aware_response = query(context_aware_prompt,role)
#         intro_text = context_aware_response.split('\n')[0].strip()

#     if use_internet: 
#         python_dict_prompt = f'''
#             Now, return the suggested materials and their detailed reasons from the previous response as a Python dictionary. 
#             The keys are the names of the suggested materials, and the values are the detailed reasons. The detailed reasons should be written using Markdown.
#             Make sure the reasons are the same as the ones in the previous response, and maintain their reference citations.
#             Do not say anything else apart from the dictionary.
#         '''
#     else: 
#         python_dict_prompt= '''
#         Now, return the suggested materials and their detailed reasons as a Python dictionary. 
#         The keys are the names of the suggested materials, and the values are the detailed reasons. The detailed reasons should be written using Markdown.
#         Make sure the reasons are the same as the ones in the previous response.
#         Do not say anything else apart from the dictionary.'''
#     python_dict_response = query(python_dict_prompt,role).strip()
#     end_time = time.time()
#     print(f"Time elapsed: {end_time-start_time} seconds.")

#     # Remove text before and after the Python list
#     start_index = python_dict_response.find('{')
#     if start_index>0:
#         print("Removing text before the Python list.")
#         python_dict_response = python_dict_response[start_index:].strip()
#     end_index = python_dict_response.rfind('}')
#     if end_index<len(python_dict_response)-1:
#         print("Removing text after the Python list.")
#         python_dict_response = python_dict_response[:end_index+1].strip()

#     python_dict_response = python_dict_response.strip()

#     try:
#         suggestions = ast.literal_eval(python_dict_response)
#     except SyntaxError as e:
#         intro_text = f"Sorry, please try again. We got the following error: {e}."
#         suggestions = {}
#     return intro_text, suggestions
# '''
# attached_parts: list of tuples (object_name, part_name, material_name)
# '''
# def provide_material_feedback(material_name, object_name, part_name, use_internet=False, attached_parts=None, design_brief=None):
    
#     feedback_model = "gpt-3.5-turbo-16k"
#     aspects = ["durability", "maintenance", "sustainability", "assembly", "cost", "availability"]
#     if(object_name==part_name):
#         part_name=""
#     material_feedback_prompt_head = f"I have a {object_name} {part_name} made out of {material_name}. "

#     materials_context=""
#     if attached_parts is not None and len(attached_parts)>0:
#         materials_context = f'''Here is additional information on other parts it is attached to for context: \n'''
#         for attached_part in attached_parts:
#             parent = attached_part[0]
#             part=attached_part[1]
#             if parent==part:
#                 materials_context += f'''It is attached to a {attached_part[0]} made out of {attached_part[2]}. '''
#             else:
#                 materials_context += f'''It is attached to a {attached_part[0]} {attached_part[1]} made out of {attached_part[2]}. '''

#     material_feedback_prompt_tail = f'''\nPlease provide feedback on the material used based on the following aspects: {", ".join(aspects[:-1])} {", and " + aspects[-1]}. 
#     For each aspect, if you gave critical feedback on that aspect, please provide up to 5 suggestions 
#     (e.g. alternative materials, adding material finishes, assembly attachments) to improve the aspect. 
#     Make sure that you also consider the object the material is used on.
#     '''
    
#     if use_internet:
#         results = []
#         material_feedback_prompt_tail += f'''\n 
#         Here are sources from the internet that you can refer to and cite when providing feedback: \n
#         '''
#         src_idx=1
#         references = []
#         for i in range(len(aspects)):
#             aspect = aspects[i]
#             internet_search_query = f'{aspect} of a {object_name} {part_name} made out of {material_name}'
#             _, results = internet_search(internet_search_query,role="user",n_results=5)
#             material_feedback_prompt_tail += f"**{aspect}**:"
#             for r in results:
#                 material_feedback_prompt_tail += f'''\n
#                 NUMBER:{src_idx}
#                 URL:{r['link']}
#                 TITLE:{r['title']}
#                 CONTENT:{r['snippet']}
#                 '''
#                 references.append({
#                     "number":src_idx,
#                     "url":r['link'],
#                     "title":r['title'],
#                 })
#                 src_idx+=1
#         material_feedback_prompt_tail += f'''
#         Make sure to cite results using [[NUMBER](URL)] notation after the reference. 
#         If the provided information from the internet results refers to multiple subjects with the same name, write separate answers for each subject.
#         '''

#     material_feedback_prompt = material_feedback_prompt_head + materials_context + material_feedback_prompt_tail +  "\nRespond using Markdown."
#     # print(material_feedback_prompt)
#     global init_history
#     init_history_clone = copy.deepcopy(init_history)
#     init_history_clone.append({"role":"user", "content":material_feedback_prompt})

    
#     response = openai.ChatCompletion.create(
#         model=feedback_model,
#         messages=init_history_clone,
#         temperature=0.1
#     )

#     material_feedback = response["choices"][0]["message"]["content"]
#     init_history_clone.append({"role":"assistant", "content":material_feedback})
#     intro_text = material_feedback.split('\n')[0].strip()

#     if design_brief: 
#         context_aware_prompt = f''' 
#         Now, I want you to answer again but consider the following design brief for context:
#         ==========================
#         {design_brief}.
#         ==========================
#         Some parts of the design brief may be relevant to the question or instruction, while others may not be relevant.
#         '''
#         if use_internet:
#             context_aware_prompt += '''
#             You may refer to the sources retrieved from the internet in the previous message.
#             Make sure to cite results using [[NUMBER](URL)] notation after the reference.
#             Make sure that you answer the question or fulfill the instruction by both using the sources from the internet and also in the context of the design brief.
#             '''
#         else: 
#             context_aware_prompt += '''
#             Make sure that you answer the question or fulfill the instruction in the context of the design brief.
#             '''
#         init_history_clone.append({"role":"user", "content":context_aware_prompt})
        
#         context_aware_feedback_start_time=time.time()
#         context_aware_response = openai.ChatCompletion.create(
#             model=feedback_model,
#             messages=init_history_clone,
#             temperature=0.7
#         )
#         context_aware_feedback_end_time=time.time()
#         context_aware_feedback_time = context_aware_feedback_end_time-context_aware_feedback_start_time
#         print(f"Context-aware feedback time: {context_aware_feedback_time}")
#         context_aware_feedback = context_aware_response["choices"][0]["message"]["content"]
#         init_history_clone.append({"role":"assistant", "content":context_aware_feedback})
#         intro_text = context_aware_feedback.split('\n')[0].strip()


#     #########################################
#     follow_up_prompt = f'''
#     Based on the feedback, return a Python dictionary. Each key should be an aspect. The values of each aspect are "feedback" and "suggestions".
#     "feedback" is the key to the feedback you provided for that aspect. Make sure that the feedback is in Markdown format and it is exactly the same as the feedback you provided for that aspect in the previous response.
#     "suggestions" is a list of lists where each list contains the name of the suggested item and item type.
#     The item type must either be one of the following: material, finish, attachment, or other.
#     Here is a template:
#     '''

#     dict_template2 = {}
#     for i in range(len(aspects)):
#         aspect = aspects[i]
#         dict_template2[aspect] = {
#             "feedback": f"{aspect} feedback",
#             "suggestions": [["item1","item_type"], ["item2","item_type"]]
#         }

#     dict_template_str = json.dumps(dict_template2, indent=4)
#     follow_up_prompt += dict_template_str
#     init_history_clone.append({"role":"user", "content":follow_up_prompt})
#     #########################################

#     suggestions_dict_response_start_time=time.time()
#     suggestions_dict_response = openai.ChatCompletion.create(
#         model=feedback_model,
#         messages=init_history_clone,
#         temperature=0.0
#     )
#     suggestions_dict_response_end_time=time.time()
#     suggestions_dict_response_time = suggestions_dict_response_end_time-suggestions_dict_response_start_time
#     print(f"Suggestions dict response time: {suggestions_dict_response_time}")
#     suggestions_dict_str= suggestions_dict_response["choices"][0]["message"]["content"]

#     # Remove text before and after the Python dict
#     start_index = suggestions_dict_str.find('{')
#     if start_index>0:
#         print("Removing text before the Python dictionary.")
#         suggestions_dict_str = suggestions_dict_str[start_index:].strip()
#     end_index = suggestions_dict_str.rfind('}')
#     if end_index<len(suggestions_dict_str)-1:
#         print("Removing text after the Python dictionary.")
#         suggestions_dict_str = suggestions_dict_str[:end_index+1].strip()

#     suggestions_dict_str = suggestions_dict_str.strip()

#     try:
#         suggestions_dict= ast.literal_eval(suggestions_dict_str)
#     except SyntaxError as e:
#         intro_text = f"Sorry, please try again. We got the following error: {e}."
#         suggestions_dict = {}
#     return intro_text, material_feedback, suggestions_dict, references



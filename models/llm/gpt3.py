
import os, copy
import openai, tiktoken
openai.api_key=os.getenv("OPENAI_API_KEY") #If first time using this repo, set the environment variable "OPENAI_API_KEY", to your API key from OPENAI
import re , ast, json
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
search = DuckDuckGoSearchResults(num_results=10)

message_history = []
temperature=0.0
model_name = "gpt-3.5-turbo"
max_tokens=4097
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
    if model == "gpt-3.5-turbo":
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

def internet_search(query,role="user"):
    global message_history 

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
    return prompt

def query(prompt,role="user"):
    global message_history
    message_history.append({"role":role, "content":prompt})
    check_and_trim_message_history()
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=message_history,
        temperature=temperature
    )
    response_msg = response["choices"][0]["message"]["content"]
    message_history.append({"role":response["choices"][0]["message"]["role"], "content":response_msg})
    return response_msg

def suggest_materials(prompt,role="user", use_internet=True):
    refined_prompt = f"{prompt}"
    if use_internet:
        refined_prompt = internet_search(refined_prompt,role)
    initial_response = query(refined_prompt,role)
    intro_text = initial_response.split('\n')[0].strip()
    if use_internet: 
        python_dict_prompt = f'''
            Now, return the suggested materials and their detailed reasons from the previous response as a Python dictionary. 
            Make sure the reasons are the same as the ones in the previous response, and maintain their reference citations.
            Do not say anything else apart from the dictionary.
        '''
    else: 
        python_dict_prompt= '''
        Now, return the suggested materials and their detailed reasons as a Python dictionary. 
        Make sure the reasons are the same as the ones in the previous response.
        Do not say anything else apart from the dictionary.'''
    python_dict_response = query(python_dict_prompt,role).strip()

    # Remove text before and after the Python list
    start_index = python_dict_response.find('{')
    if start_index>0:
        print("Removing text before the Python list.")
        python_dict_response = python_dict_response[start_index:].strip()
    end_index = python_dict_response.rfind('}')
    if end_index<len(python_dict_response)-1:
        print("Removing text after the Python list.")
        python_dict_response = python_dict_response[:end_index+1].strip()

    python_dict_response = python_dict_response.strip()


    suggestions = ast.literal_eval(python_dict_response)
    return intro_text, suggestions

def suggest_color_palettes(prompt, role="user", use_internet=True):
    refined_prompt = f"{prompt}. Suggest color palettes."
    if use_internet:
        refined_prompt = internet_search(refined_prompt,role)
    initial_response = query(refined_prompt,role)
    intro_text = initial_response.split('\n')[0].strip()

    if use_internet:
        python_list_prompt='''
        Now, return the suggested color palettes that contain hex color codes, their names, and their detailed descriptions from the previous response as a Python list of dictionaries. 
        Each dictionary should contain the following keys: name, description, codes. 
        Make sure the descriptions are the same as the ones in the previous response, and maintain their reference citations.
        Do not say anything else apart from the Python list.
        '''
    else:
        python_list_prompt='''
        Now, return the suggested color palettes that contain hex color codes, their names, and their detailed descriptions from the previous response as a Python list of dictionaries. 
        Each dictionary should contain the following keys: name, description, codes. 
        Make sure the descriptions are the same as the ones in the previous response.
        Do not say anything else apart from the Python list.
        '''
    python_list_response = query(python_list_prompt,role).strip()

    # Remove text before and after the Python list
    start_index = python_list_response.find('[')
    if start_index>0:
        print("Removing text before the Python list.")
        python_list_response = python_list_response[start_index:].strip()
    end_index = python_list_response.rfind(']')
    if end_index<len(python_list_response)-1:
        print("Removing text after the Python list.")
        python_list_response = python_list_response[:end_index+1].strip()

    python_list_response = python_list_response.strip()

    suggestions = ast.literal_eval(python_list_response)
    return intro_text, suggestions

# def suggest_color_palettes(prompt, role="user"):
#     refined_prompt = f'''{prompt}. 
#     Suggest color palettes that contain hex codes using the following format:

#     - Color Palette #1 Name
#     Textual explanation of color palette
#     HEX codes: HEXCODE1, #HEXCODE2, #HEXCODE3,... #HEXCODEN

#     - Color Palette #2 Name
#     Textual explanation of color palette
#     HEX codes: HEXCODE1, #HEXCODE2, #HEXCODE3,... #HEXCODEN

#     .....

#     - Color Palette #N Name
#     Textual explanation of color palette
#     HEX codes: HEXCODE1, #HEXCODE2, #HEXCODE3,... #HEXCODEN

#     Now, suggest 5 color palettes.
#     '''

#     initial_response = query(refined_prompt,role)
#     intro_text = initial_response.split('\n')[0].strip()

#     python_list_prompt= '''
#         Now, return them as a Python list of dictionaries. 
#         Each dictionary should contain the following keys: name, description, codes. 
#         RETURN THE PYTHON LIST ONLY. Do not say anything else (ex. "Here are the color palettes you requested, return as a list of dictionaries.") apart from the Python list.
#     '''

#     python_list_response = query(python_list_prompt,role)

#     python_list = ast.literal_eval(python_list_response)
#     return intro_text, python_list

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
    keywords = ast.literal_eval(response["choices"][0]["message"]["content"])
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

    prompts = ast.literal_eval(python_list_response["choices"][0]["message"]["content"])

    return prompts


materials_feedbacks = []
'''
attached_parts: list of tuples (object_name, part_name, material_name)
'''
def provide_material_feedback(material_name, object_name, part_name, attached_parts=None, design_context=None):
    material_feedback_prompt_head = f'''
    I have a {object_name} {part_name} made out of {material_name}. 
    '''

    materials_context = f'''Here is additional information for context: \n'''
    if attached_parts is not None:
        for attached_part in attached_parts:
            materials_context += f'''It is attached to a {attached_part[0]} {attached_part[1]} made out of {attached_part[2]}. '''

    material_feedback_prompt_tail = f'''\n
        Please provide feedback on the material used based on the following aspects: durability, maintenance, sustainability, assembly, and cost. 
        For each aspect, if you gave critical feedback on that aspect, please provide up to 5 suggestions 
        (e.g. alternative materials, adding material finishes, assembly attachments) to improve the aspect. 
        Make sure that you also consider the object the material is used on.

        Respond using Markdown.
    '''

    material_feedback_prompt = material_feedback_prompt_head + materials_context + material_feedback_prompt_tail
    print(material_feedback_prompt)

    global init_history
    init_history_clone = copy.deepcopy(init_history)
    init_history_clone.append({"role":"user", "content":material_feedback_prompt})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=init_history_clone,
        temperature=0.1
    )

    material_feedback = response["choices"][0]["message"]["content"]
    init_history_clone.append({"role":"assistant", "content":material_feedback})

    follow_up_prompt = f'''
        Based on the feedback, for each aspect, if you mentioned any materials, finishes, or assembly attachments, return them as a dictionary. 
        The keys should be the aspects, and the values in each aspect is a list of mentioned items. Here is a template:
    '''
    dict_template = {
            "durability": ["finish1", "finish2", "material1","material2"],
            "maintenance": ["finish1", "finish2", "material1","material2"],
            "sustainability": ["material1","material2"],
            "assembly": ["assembly_attachment_1", "assembly_attachment_2"],
            "cost": ["material1","material2"]
    }
    dict_template_str = json.dumps(dict_template)
    follow_up_prompt += dict_template_str
    print(follow_up_prompt)



    return material_feedback


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


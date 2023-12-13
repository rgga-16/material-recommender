'''
Based on tutorial from
https://medium.com/artificialis/build-your-own-chatgpt-bot-with-internet-access-and-memory-using-langchain-and-gradio-977f025b1258


ChatGPT API

Search Tools
https://python.langchain.com/en/latest/modules/agents/tools/examples/google_search.html 
https://python.langchain.com/en/latest/modules/agents/tools/examples/ddg.html 
https://python.langchain.com/en/latest/modules/agents/tools/examples/brave_search.html 
https://python.langchain.com/en/latest/modules/agents/tools/examples/search_tools.html 
'''

import os, ast
from datetime import datetime
from langchain.agents import Tool
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.tools import DuckDuckGoSearchRun
from langchain.tools import DuckDuckGoSearchResults
from langchain.tools import BraveSearch
from langchain.agents import initialize_agent
import gradio as gr

from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)


from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY =os.getenv("OPENAI_API_KEY")
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")

def suggest_color_palettes(input_text):
    input_text+= "Suggest color palettes."
    
    # prompt=f'''
    #     Disregard any previous instructions.

    #     I will give you a question or an instruction. Your objective is to answer my question or fulfill my instruction.

    #     My question or instruction is: {input_text}

    #     For your reference, today's date is {datetime.now().isoformat()}.

    #     It's possible that the question or instruction, or just a portion of it, requires relevant information from the internet to give a satisfactory answer or complete the task. 
    #     Therefore, provided below is the necessary information obtained from the internet, which sets the context for addressing the question or fulfilling the instruction. 
    #     You will write a comprehensive reply to the given question or instruction. 
    #     Make sure to cite results using [[NUMBER](URL)] notation after the reference. 
    #     If the provided information from the internet results refers to multiple subjects with the same name, write separate answers for each subject:
    # '''
    # results_str= search.run(input_text)
    # results = ast.literal_eval(results_str)

    # for i in range(len(results)):
    #     r = results[i]
    #     prompt += f'''\n
    #         NUMBER:{i+1}
    #         URL:{r['link']}
    #         TITLE:{r['title']}
    #         CONTENT:{r['snippet']}
    #     '''

    prompt = input_text
    
    messages=[{"role":"user", "content":prompt}]

    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=messages,
    temperature=0.0)

    response_msg = response["choices"][0]["message"]["content"]
    intro_text = response_msg.split("\n")[0].strip()
    messages.append({"role":response["choices"][0]["message"]["role"], "content":response_msg})
    
    python_dict_prompt= '''
    Now, return the suggested color palettes that contain hex color codes, their names, and their detailed reasons from the previous response as a Python list of dictionaries. 
    Each dictionary should contain the following keys: name, description, codes. 
    Make sure the reasons are the same as the ones in the previous response, and maintain their reference citations.
    Do not say anything else apart from the Python list.
    '''

    messages.append({"role":"user", "content":python_dict_prompt})
    dict_response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=messages,
    temperature=0.0)
    dict_response_msg = dict_response["choices"][0]["message"]["content"]

    final_message = f'''
        {response_msg}
        \n\n
        ======================
        \n\n
        {intro_text}
        {dict_response_msg}
    '''

    return final_message

def suggest_materials(input_text):
    prompt=f'''
        Disregard any previous instructions.

        I will give you a question or an instruction. Your objective is to answer my question or fulfill my instruction.

        My question or instruction is: {input_text}

        For your reference, today's date is {datetime.now().isoformat()}.

        It's possible that the question or instruction, or just a portion of it, requires relevant information from the internet to give a satisfactory answer or complete the task. 
        Therefore, provided below is the necessary information obtained from the internet, which sets the context for addressing the question or fulfilling the instruction. 
        You will write a comprehensive reply to the given question or instruction. 
        Make sure to cite results using [[NUMBER](URL)] notation after the reference. 
        If the provided information from the internet results refers to multiple subjects with the same name, write separate answers for each subject:
    '''
    results_str= search.run(input_text)
    results = ast.literal_eval(results_str)

    for i in range(len(results)):
        r = results[i]
        prompt += f'''\n
            NUMBER:{i+1}
            URL:{r['link']}
            TITLE:{r['title']}
            CONTENT:{r['snippet']}
        '''

    messages=[{"role":"user", "content":prompt}]

    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=messages,
    temperature=0.0)

    response_msg = response["choices"][0]["message"]["content"]
    intro_text = response_msg.split("\n")[0].strip()
    messages.append({"role":response["choices"][0]["message"]["role"], "content":response_msg})

    python_dict_prompt= '''
    Now, return the suggested materials and their detailed reasons from the previous response as a Python dictionary. 
    Make sure the reasons are the same as the ones in the previous response, and maintain their reference citations.
    Do not say anything else apart from the dictionary.
    '''
    messages.append({"role":"user", "content":python_dict_prompt})
    dict_response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=messages,
    temperature=0.0)
    dict_response_msg = dict_response["choices"][0]["message"]["content"]

    final_message = f'''
        {response_msg}
        \n\n
        ======================
        \n\n
        {intro_text}
        {dict_response_msg}
    '''

    return final_message


# Using DuckDuckGoSearchRun
search = DuckDuckGoSearchResults(num_results=5)
tools = [
    Tool(name="Search", func=search.run, description="useful when you need to answer questions about current events")
]

interface = gr.Interface(fn=suggest_color_palettes, inputs="text", outputs="text", description="Chat with a conversational agent")

interface.launch(share=True)


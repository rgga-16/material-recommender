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

import openai


from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY =os.getenv("OPENAI_API_KEY")
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
openai.api_key=OPENAI_API_KEY

def chat_response(input_text):
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

    message=[{"role":"user", "content":prompt}]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=message,
        temperature=0.0
    )

    response_msg = response["choices"][0]["message"]["content"]
    return response_msg


# Using DuckDuckGoSearchRun
search = DuckDuckGoSearchResults(num_results=5)
tools = [
    Tool(name="Search", func=search.run, description="useful when you need to answer questions about current events")
]

interface = gr.Interface(fn=chat_response, inputs="text", outputs="text", description="Chat with a conversational agent")

interface.launch(share=True)

# Using BraveSearch
# search = BraveSearch.from_api_key(api_key=BRAVE_API_KEY, search_kwargs={"count":10})
# tools = [
#     Tool(name="Search", func=search.run, description="useful when you need to answer questions about current events")
# ]

# memory = ConversationBufferMemory(memory_key="chat_history",return_messages=True)

# llm=ChatOpenAI(temperature=0)
# agent_chain = initialize_agent(tools, llm, agent="chat-conversational-react-description",verbose=True, memory=memory)

# def chat_response(input_text):
#     response = agent_chain.run(input=input_text)
#     return response


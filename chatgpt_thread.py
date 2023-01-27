from threading import Thread,Event
from queue import Queue,Empty
from chatgpt_wrapper import ChatGPT


gpt = ChatGPT()

while True:
    prompt = input("\nTalk to ChatGPT! ")
    answer = gpt.ask(prompt)
    print(f'{answer}\n')
'''
Unofficial API that uses ChatGPT
References:
- https://medium.com/geekculture/using-chatgpt-in-python-eeaed9847e72
- https://github.com/mmabrouk/chatgpt-wrapper
'''

from chatgpt_wrapper import ChatGPT

bot = ChatGPT()
# return the full result
response = bot.ask("What are tables made of? Answer in bullet points.")
print(response)

# return the result in streaming (chunks)
# for chunk in bot.ask_stream("tell me a story about cats and dogs"):
#     print(chunk)
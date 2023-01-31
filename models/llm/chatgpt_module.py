from chatgpt_wrapper import ChatGPT

class ChatGPT_Bot():
    def __init__(self) -> None:
        self.conversation_id = None 
    
    def ask(self, message):

        bot = ChatGPT(headless=True,browser='firefox')
        if self.conversation_id is None:
            self.conversation_id = bot.conversation_id
        else:
            bot.page.goto(f"chat.open.ai.com/chat/{self.conversation_id}")
        response = bot.ask(message)
        bot._cleanup()

        return response


if __name__=='__main__':
    bot = ChatGPT(headless=False)
    print(bot.ask("hello"))

    while True:
        message = input("Input message here: ")
        response = bot.ask(message)
        print(f"ChatGPT: {response}\n")


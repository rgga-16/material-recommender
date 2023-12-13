import openai, os, base64, requests 
from openai import OpenAI
import json
 #If first time using this repo, set the environment variable "OPENAI_API_KEY", to your API key from OPENAI


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def main():

    image_path ="./sidetable.png"
    b64_image = encode_image(image_path)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}",
    }

    prompt = '''
        Pretend you are DALL-E. You are given an image containing a side table. 
        Make an image prompt that will generate a texture map of oak wood that will be suitable specifically for the side table in the image.
        Use as many keywords as you need to get the best result.
        The prompt should follow this format:

        "oak wood, <keyword_1>, <keyword_2>, ....., <keyword_n>, texture map, seamless, 4k"

    '''

    payload = {
        "model":"gpt-4-vision-preview",
        "messages":[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                    "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{b64_image}"
                        },
                    },
                ],
            }
        ],
        "max_tokens":300,
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)

    json_response = response.json()
    content = json_response['choices'][0]['message']['content']

    # Prompt generated: oak wood, fine grain, natural finish, furniture-grade, contemporary design, texture map, seamless, 4k


    return 

if __name__ == "__main__":
    main()
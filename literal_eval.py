
import ast,os
import openai
openai.api_key=os.getenv("OPENAI_API_KEY") #If first time using this repo, set the environment variable "OPENAI_API_KEY", to your API key from OPENAI

system_prompt = '''
    I want you to act as an interior and furniture design expert with expert knowledge of materials. Your role is to:

    1) Suggest materials and color palettes when asked, depending on the criteria to suggest them.
    2) Provide feedback on materials when asked, depending on the criteria to provide feedback.
'''

message_history = [{"role":"system", "content":system_prompt}]

def query(prompt,role="user"):

    global message_history
    message_history.append({"role":role, "content":prompt})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=message_history,
        temperature=0.1
    )

    response_msg = response["choices"][0]["message"]["content"]
    message_history.append({"role":response["choices"][0]["message"]["role"], "content":response_msg})

    return response_msg

def suggest_materials(prompt):
    refined_prompt = f"{prompt}"
    initial_response = query(refined_prompt,role="user")

    intro_text = initial_response.split('\n')[0].strip()

    python_dict_prompt= "Now, return the suggestions as a Python dictionary. Do not say anything else apart from the dictionary."
    python_dict_response = query(python_dict_prompt,role="user")

    suggestions = ast.literal_eval(python_dict_response)


    return intro_text, suggestions
    print()

prompts=[
    "What are some durable and low-maintenance materials that I can use for my outdoor patio furniture?",
    "Can you suggest some eco-friendly and sustainable materials for my living room renovation project?",
    "I'm on a tight budget, can you suggest some affordable materials for my kitchen countertop?"
]

# suggest_materials(prompts[0])

string = '''
    Sure, here is the list of dictionaries:

```
[
    {
        "name": "Minimalist Monochrome",
        "description": "This palette features a minimalistic black and white color scheme that is timeless and modern. It works well with natural materials like wood and stone.",
        "codes": ["#FFFFFF", "#000000"]
    },
    {
        "name": "Serene Neutrals",
        "description": "This palette features soft neutral tones that create a calming and serene environment. It works well with organic materials like linen and wool.",
        "codes": ["#F7F7F7", "#E5E5E5", "#D2D2D2", "#BABABA", "#A2A2A2"]
    },
    {
        "name": "Bold Accents",
        "description": "This palette features a neutral base with bold accent colors that add a pop of color and personality. It works well with metallic materials like brass and copper.",
        "codes": ["#FFFFFF", "#000000", "#FFC857", "#E9724C", "#C5283D"]
    },
    {
        "name": "Earthy Tones",
        "description": "This palette features rich earthy tones that create a warm and inviting atmosphere. It works well with natural materials like leather and rattan.",
        "codes": ["#D6C9A9", "#8D6E63", "#4E342E", "#A1887F", "#EFE0CE"]
    },
    {
        "name": "Moody Blues",
        "description": "This palette features deep blues and grays that create a moody and sophisticated atmosphere. It works well with materials like velvet and marble.",
        "codes": ["#1C1C1E", "#3A3A3C", "#5C5C5E", "#8A8A8D", "#B8B8BB"]
    }
]
```

'''
thing = ast.literal_eval(string)
print()
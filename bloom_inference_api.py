
'''
Watch tutorial: https://www.youtube.com/watch?v=5ef83Wljm-M
'''

import requests,copy
from tqdm import tqdm

API_URL = "https://api-inference.huggingface.co/models/bigscience/bloom"
headers = {"Authorization": "Bearer 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"}

def iterative_query(prompt, n_tokens=4000,n_tokens_per_query=250):

	for i in range(0,n_tokens,n_tokens_per_query):
		input_dict = {
			"inputs": prompt,
			"max_new_tokens": f"{n_tokens_per_query}",
			"do_sample": False 
		}
		response = get_response(input_dict)[0]

		if 'generated_text' in list(response.keys()):
			prompt=response['generated_text']
			print()
	
	if 'generated_text' in list(response.keys()):
		response = response['generated_text']
	return response

def get_response(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()

if __name__=="__main__":

	query = "The best types of wood materials for furniture available in the Philippines are"
		
	output = query(query)
	print(output)
	print()
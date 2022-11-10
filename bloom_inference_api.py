import requests

API_URL = "https://api-inference.huggingface.co/models/bigscience/bloom"
headers = {"Authorization": "Bearer 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"}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()


input_dict = {
	# "inputs": "The best types of wood materials for furniture available in the Philippines are",
	"inputs":"The best types of wood materials for furniture available in the Philippines are",
	"max_new_tokens": "250",
}
	
output = query(input_dict)
print(output)
print()
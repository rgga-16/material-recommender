from transformers import AutoTokenizer, AutoModel, set_seed, AutoModelForCausalLM
import torch
torch.set_default_tensor_type(torch.cuda.FloatTensor)

tokenizer = AutoTokenizer.from_pretrained("bigscience/bloom-1b7")

model_lm = AutoModelForCausalLM.from_pretrained("bigscience/bloom-1b7")

prompt = ""
input_tokens = tokenizer(prompt, return_tensors="pt").to(0)
result_sample = model_lm.generate(**input_tokens, max_length=200, top_k=0, temperature=0.5)
output_text = tokenizer.decode(result_sample[0], truncate_before_pattern=[r"\n\n^#", "^'''", "\n\n\n"] )
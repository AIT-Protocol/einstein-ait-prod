import einstein
from einstein.llms.hf import load_hf_pipeline, HuggingFaceLLM
from einstein.llms.hf import HuggingFacePipeline
import torch
import time
import mathgenerator as mg
import bittensor as bt
from einstein.rewards.advanced_math import AdvancedMathModel

model_kwargs = None

llm_pipeline = HuggingFacePipeline(
    model_id="EleutherAI/llemma_7b",
    torch_dtype=torch.float16,
    device="cuda" if torch.cuda.is_available() else "cpu",
    mock=False,
    model_kwargs=model_kwargs,
    )

system_prompt = """
You are an advanced Math AI Solver. Your task is to provide users with clear and concise explanations 
and answers to their math questions.
Mandatory:
- If the answer is a symbol, you must say 'So the final answer is: (that symbol)'.
- Unless not symbol, you always end the entire sentence with 'So the final answer is: (the answer)'
"""

t0 = time.time()
math_gen = mg.generate_context()
prompt = math_gen['problem']
reference = math_gen['solution']

bt.logging.debug(f"💬 Querying Cerebral: {prompt}")

llm = HuggingFaceLLM(
    llm_pipeline=llm_pipeline,
    system_prompt=system_prompt,
    max_new_tokens=1024,
    do_sample=True,
    temperature=0.9,
    top_k=50,
    top_p=0.95,
    )

response = llm.query(
        message=prompt,
        role="user",
        disregard_system_prompt=False,
        )

synapse_latency = time.time() - t0

print('*'*20)
print('Question:', prompt)
print('Answer:', response)
print('*'*20)
print('Reference:', reference)
print('Extracted Answer:', AdvancedMathModel.extract_number(response))
print('Synapse Latency:', synapse_latency)
try:
    print('Math Score:', AdvancedMathModel.math_score(response, reference))
finally:
    pass

torch.cuda.empty_cache()


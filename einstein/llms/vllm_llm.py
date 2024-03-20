import gc
import time
import torch
import bittensor as bt
from typing import List, Dict
from vllm import LLM, SamplingParams
from einstein.cleaners.cleaner import CleanerPipeline
from einstein.llms import BasePipeline, BaseLLM
from einstein.mock import MockPipeline
from einstein.llms.utils import calculate_gpu_requirements
from vllm.model_executor.parallel_utils.parallel_state import destroy_model_parallel


def clean_gpu_cache():
    destroy_model_parallel()
    gc.collect()
    torch.cuda.empty_cache()
    torch.distributed.destroy_process_group()

    # Wait for the GPU to clean up
    time.sleep(10)
    torch.cuda.synchronize()


def load_vllm_pipeline(model_id: str, device: str, mock=False):
    """Loads the VLLM pipeline for the LLM, or a mock pipeline if mock=True"""
    if mock or model_id == "mock":
        return MockPipeline(model_id)

    # Calculates the gpu memory utilization required to run the model within 20GB of GPU
    max_allowed_memory_in_gb = 20
    max_allowed_memory_allocation_in_bytes = max_allowed_memory_in_gb * 1e9
    gpu_mem_utilization = calculate_gpu_requirements(
        device, max_allowed_memory_allocation_in_bytes
    )

    try:
        # Attempt to initialize the LLM
        return LLM(model=model_id, gpu_memory_utilization=gpu_mem_utilization)
    except ValueError as e:
        bt.logging.error(
            f"Error loading the VLLM pipeline within {max_allowed_memory_in_gb}GB: {e}"
        )

    # If the first attempt fails, retry with increased memory allocation
    try:
        bt.logging.info(
            "Trying to cleanup GPU and retrying to load the model with extra allocation..."
        )
        # Clean the GPU from memory before retrying
        clean_gpu_cache()

        # Increase the memory allocation for the second attempt
        max_allowed_memory_in_gb_second_attempt = 24
        max_allowed_memory_allocation_in_bytes = (
            max_allowed_memory_in_gb_second_attempt * 1e9
        )
        bt.logging.warning(
            f"Retrying to load with {max_allowed_memory_in_gb_second_attempt}GB..."
        )
        gpu_mem_utilization = calculate_gpu_requirements(
            device, max_allowed_memory_allocation_in_bytes
        )

        # Attempt to initialize the LLM again with increased memory allocation
        return LLM(model=model_id, gpu_memory_utilization=gpu_mem_utilization)
    except Exception as e:
        bt.logging.error(
            f"Error loading the VLLM pipeline within {max_allowed_memory_in_gb_second_attempt}GB: {e}"
        )
        raise e


class vLLMPipeline(BasePipeline):
    def __init__(self, model_id: str, device: str = None, mock=False):
        super().__init__()
        self.llm = load_vllm_pipeline(model_id, device, mock)
        self.mock = mock

    def __call__(self, composed_prompt: str, **model_kwargs: Dict) -> str:
        if self.mock:
            return self.llm(composed_prompt, **model_kwargs)

        # Compose sampling params
        temperature = model_kwargs.get("temperature", 0.8)
        top_p = model_kwargs.get("top_p", 0.95)
        max_tokens = model_kwargs.get("max_tokens", 256)

        sampling_params = SamplingParams(
            temperature=temperature, top_p=top_p, max_tokens=max_tokens
        )
        output = self.llm.generate(composed_prompt, sampling_params, use_tqdm=True)
        response = output[0].outputs[0].text
        return response


class vLLM_LLM(BaseLLM):
    def __init__(
        self,
        llm_pipeline: BasePipeline,
        system_prompt,
        max_new_tokens=256,
        temperature=0.7,
        top_p=0.95,
    ):
        model_kwargs = {
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_new_tokens,
        }
        super().__init__(llm_pipeline, system_prompt, model_kwargs)

        # Keep track of generation data using messages and times
        self.messages = [{"content": self.system_prompt, "role": "system"}]
        self.times = [0]

    def query(
        self,
        message: str,
        role: str = "user",
        disregard_system_prompt: bool = False,
        cleaner: CleanerPipeline = None,
    ):
        # Adds the message to the list of messages for tracking purposes, even though it's not used downstream
        messages = self.messages + [{"content": message, "role": role}]

        t0 = time.time()
        response = self.forward(messages=messages)
        response = self.clean_response(cleaner, response)

        self.messages = messages + [{"content": response, "role": "assistant"}]
        self.times = self.times + [0, time.time() - t0]

        return response

    def _make_prompt(self, messages: List[Dict[str, str]]):
        composed_prompt = ""

        for message in messages:
            if message["role"] == "system":
                composed_prompt += f'<|system|>{message["content"]} '
            elif message["role"] == "user":
                composed_prompt += f'<|user|>{message["content"]} '
            elif message["role"] == "assistant":
                composed_prompt += f'<|assistant|>{message["content"]} '

        # Adds final tag indicating the assistant's turn
        composed_prompt += "<|assistant|>"
        return composed_prompt

    def forward(self, messages: List[Dict[str, str]]):
        # make composed prompt from messages
        composed_prompt = self._make_prompt(messages)
        response = self.llm_pipeline(composed_prompt, **self.model_kwargs)

        bt.logging.info(
            f"{self.__class__.__name__} generated the following output:\n{response}"
        )

        return response


if __name__ == "__main__":
    # Example usage
    llm_pipeline = vLLMPipeline(
        model_id="HuggingFaceH4/zephyr-7b-beta", device="cuda", mock=False
    )
    llm = vLLM_LLM(llm_pipeline, system_prompt="You are a helpful AI assistant")

    message = "What is the capital of Texas?"
    response = llm.query(message)
    print(response)

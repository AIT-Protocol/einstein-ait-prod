import time

from typing import List, Dict
import bittensor as bt

from transformers import Pipeline, pipeline
from einstein.mock import MockPipeline

from einstein.cleaners.cleaner import CleanerPipeline


def load_pipeline(
    model_id, device=None, torch_dtype=None, mock=False, model_kwargs: dict = None
):
    """Loads the HuggingFace pipeline for the LLM, or a mock pipeline if mock=True"""

    if mock or model_id == "mock":
        return MockPipeline(model_id)

    if not device.startswith("cuda"):
        bt.logging.warning("Only crazy people run this on CPU. It is not recommended.")

    # model_kwargs torch type definition conflicts with pipeline torch_dtype, so we need to differentiate them
    if model_kwargs is None:
        llm_pipeline = pipeline(
            "text-generation",
            model=model_id,
            device=device,
            torch_dtype=torch_dtype,
        )
    else:
        llm_pipeline = pipeline(
            "text-generation",
            model=model_id,
            device_map=device,
            model_kwargs=model_kwargs,
        )

    return llm_pipeline


class HuggingFaceLLM:
    def __init__(
        self,
        llm_pipeline: Pipeline,
        system_prompt,
        max_new_tokens=256,
        do_sample=True,
        temperature=0.7,
        top_k=50,
        top_p=0.95,
    ):
        self.llm_pipeline = llm_pipeline
        self.system_prompt = system_prompt
        self.kwargs = dict(
            do_sample=do_sample,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            max_new_tokens=max_new_tokens,
        )

        self.messages = [{"content": self.system_prompt, "role": "system"}]
        self.times = [0]

    def query(
        self,
        message: List[Dict[str, str]],
        role: str = "user",
        disregard_system_prompt: bool = False,
        cleaner: CleanerPipeline = None,
    ):
        messages = self.messages + [{"content": message, "role": role}]

        if disregard_system_prompt:
            messages = messages[1:]

        tbeg = time.time()
        response = self.forward(messages=messages)

        if cleaner is not None:
            clean_response = cleaner.apply(generation=response)
            if clean_response != response:
                bt.logging.debug(
                    f"Response cleaned, chars removed: {len(response) - len(clean_response)}..."
                )
            response = clean_response

        self.messages = messages + [{"content": response, "role": "assistant"}]
        self.times = self.times + [0, time.time() - tbeg]

        return response


    def queryTemp(
        self,
        message: str,
        disregard_system_prompt: bool = False,
        cleaner: CleanerPipeline = None,
    ):
        messages = self.messages + [{"content": message, "role": "user"}]

        if disregard_system_prompt:
            messages = messages[1:]

        tbeg = time.time()
        response = self.forward(messages=messages)

        if cleaner is not None:
            clean_response = cleaner.apply(generation=response)
            if clean_response != response:
                bt.logging.debug(
                    f"Response cleaned, chars removed: {len(response) - len(clean_response)}..."
                )
            response = clean_response

        self.messages = messages + [{"content": response, "role": "assistant"}]
        self.times = self.times + [0, time.time() - tbeg]

        return response

    def __call__(self, messages: List[Dict[str, str]]):
        return self.forward(messages=messages)

    def _make_prompt(self, messages: List[Dict[str, str]]):
        return self.llm_pipeline.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

    def forward(self, messages: List[Dict[str, str]], preformat_messages: bool = False):
        prompt = self._make_prompt(messages)
        outputs = self.llm_pipeline(prompt, **self.kwargs)
        response = outputs[0]["generated_text"]

        response = response.replace(prompt, "").strip()

        bt.logging.info(
            f"{self.__class__.__name__} generated the following output:\n{response}"
        )
        return response

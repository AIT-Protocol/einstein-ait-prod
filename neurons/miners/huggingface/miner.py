import time
import torch
import argparse
import bittensor as bt
from functools import partial
from starlette.types import Send
from typing import Awaitable
import urllib.parse

# Bittensor Miner Template:
from einstein.utils.config import add_hf_miner_args, add_miner_args
from einstein.protocol import StreamCoreSynapse
from einstein.llms import HuggingFaceLLM, HuggingFacePipeline, load_hf_pipeline

# import base miner class which takes care of most of the boilerplate
from einstein.base.einstein_miner import BaseStreamMiner
from deprecated import deprecated  # type: ignore


@deprecated(
    version="2.0.3+",
    reason="Class is deprecated, use openai miner for reference on example miner.",
)
class HuggingFaceMiner(BaseStreamMiner):
    """
    Base miner which runs Zephyr (https://huggingface.co/HuggingFaceH4/zephyr-7b-beta)    
    This requires a GPU with at least 62GB of memory.
    To run this miner from the project root directory:
    
    pm2 start neurons/miners/huggingface/miner.py \
    --name "hf_miner" \
    --interpreter "python" \
    -- --netuid <netuid> \
    --subtensor.network <network> \
    --wallet.name <wallet_name> \
    --wallet.hotkey <wallet_hotkey> \
    --axon.port <port> \
    --axon.external_port <port> \
    --logging.debug True \
    --neuron.model_id HuggingFaceH4/zephyr-7b-beta \
    --neuron.max_tokens 1024 \
    --neuron.do_sample True \
    --wandb.on True \
    --wandb.entity {your entity} \
    --wandb.project_name {your project name}
    """

    @classmethod
    def add_args(cls, parser: argparse.ArgumentParser):
        """
        Adds arguments to the command line parser.
        """
        super().add_args(parser)
        add_hf_miner_args(cls, parser)

    def __init__(self, config=None):
        super().__init__(config=config)

        model_kwargs = None
        if self.config.neuron.load_in_8bit:
            bt.logging.info("Loading 8 bit quantized model...")
            model_kwargs = dict(
                torch_dtype=torch.float16,
                load_in_8bit=True,
            )

        if self.config.neuron.load_in_4bit:
            bt.logging.info("Loading 4 bit quantized model...")
            model_kwargs = dict(
                torch_dtype=torch.float32,
                load_in_4bit=True,
            )

        if self.config.wandb.on:
            self.identity_tags = ("hf_miner",)

            if self.config.neuron.load_in_8bit:
                self.identity_tags += ("8bit_quantization",)
            elif self.config.neuron.load_in_4bit:
                self.identity_tags += ("4bit_quantization",)

        # Forces model loading behaviour over mock flag
        mock = (
            False if self.config.neuron.should_force_model_loading else self.config.mock
        )

        self.llm_pipeline = HuggingFacePipeline(
            model_id=self.config.neuron.model_id,
            torch_dtype=torch.bfloat16,
            device=self.device,
            mock=mock,
            model_kwargs=model_kwargs,
        )

        self.model_id = self.config.neuron.model_id
        # self.system_prompt = self.config.neuron.system_prompt
        self.system_prompt = """
        You are an advanced Math AI Solver. Your task is to provide users with clear and concise explanations 
        and answers to their math questions.
        After the generation you must end the generation with 'The final answer is: {the answer}'.
        Example:
        - User's Question ask: How do I solve for x in the equation 2x + 3 = 7?"},
        - Response:
        To solve for x in the equation 2x + 3 = 7
        We first subtract 3 from both sides of the equation to get 2x = 4.
        Then, we divide both sides by 2 to find x = 2.
        The final answer is: 2"
        """

    def forward(self, synapse: StreamCoreSynapse) -> Awaitable:
        async def _forward(
            self,
            prompt: str,
            init_time: float,
            timeout_threshold: float,
            send: Send,
        ):
            """
            Args:
                prompt (str): The received message (challenge) in the synapse. For logging.
                thread (Thread): A background thread that is reponsible for running the model.
                init_time (float): Initial time of the forward call. For timeout calculation.
                timeout_threshold (float): The amount of time that the forward call is allowed to run. If timeout is reached, streaming stops and
                    validators recieve a partial response.
                streamer (CustomTextIteratorStreamer): Iterator that holds tokens within a background Queue to be returned when sampled.
                send (Send): bittensor aiohttp send function to send the response back to the validator.
            """

            buffer = []
            temp_completion = ""  # for wandb logging
            timeout_reached = False
            system_message = ""

            # Get the math question from the last message
            role = synapse.roles[-1]
            raw_message = synapse.messages[-1]
            message = urllib.parse.parse_qs(raw_message)
            math_question = message.get("question_text", [""])[0]
            message_type = message.get("question_type", [""])[0]

            # prompt = math_question
            bt.logging.debug(f"📧 Message received, forwarding synapse: {synapse}")

            try:
                streamer = HuggingFaceLLM(
                    llm_pipeline=self.llm_pipeline,
                    system_prompt=self.system_prompt,
                    max_new_tokens=self.config.neuron.max_tokens,
                    do_sample=self.config.neuron.do_sample,
                    temperature=self.config.neuron.temperature,
                    top_k=self.config.neuron.top_k,
                    top_p=self.config.neuron.top_p,
                ).stream(message=prompt)

                bt.logging.debug("Starting streaming loop...")
                synapse_message = synapse.messages[-1]
                for token in streamer:
                    system_message += token

                    buffer.append(token)
                    system_message += "".join(buffer)

                    if synapse_message in system_message:
                        # Cleans system message and challenge from model response
                        bt.logging.warning(
                            f"Discarding initial system_prompt / user prompt inputs from generation..."
                        )
                        buffer = []
                        system_message = ""
                        continue

                    if time.time() - init_time > timeout_threshold:
                        bt.logging.debug(f"⏰ Timeout reached, stopping streaming")
                        timeout_reached = True
                        break

                    if len(buffer) == self.config.neuron.streaming_batch_size:
                        joined_buffer = "".join(buffer)
                        temp_completion += joined_buffer
                        # bt.logging.debug(f"Streamed tokens: {joined_buffer}")

                        await send(
                            {
                                "type": "http.response.body",
                                "body": joined_buffer.encode("utf-8"),
                                "more_body": True,
                            }
                        )
                        buffer = []

                if (
                    buffer and not timeout_reached
                ):  # Don't send the last buffer of data if timeout.
                    joined_buffer = "".join(buffer)
                    temp_completion += joined_buffer
                    # bt.logging.debug(f"Streamed tokens: {joined_buffer}")

                    await send(
                        {
                            "type": "http.response.body",
                            "body": joined_buffer.encode("utf-8"),
                            "more_body": False,
                        }
                    )

            except Exception as e:
                bt.logging.error(f"Error in forward: {e}")
                if self.config.neuron.stop_on_forward_exception:
                    self.should_exit = True

            finally:
                # _ = task.result() # wait for thread to finish
                bt.logging.debug("Finishing streaming loop...")
                bt.logging.debug("-" * 50)
                bt.logging.debug(f"---->>> Received message:")
                bt.logging.debug(synapse.messages[0])
                bt.logging.debug("-" * 50)
                bt.logging.debug(f"<<<----- Returned message:")
                bt.logging.debug(temp_completion)
                bt.logging.debug("-" * 50)

                synapse_latency = time.time() - init_time

                if self.config.wandb.on:
                    self.log_event(
                        timing=synapse_latency,
                        prompt=prompt,
                        completion=temp_completion,
                        system_prompt=self.system_prompt,
                    )

        # bt.logging.debug(f"📧 Message received, forwarding synapse: {synapse}")
        prompt = synapse.messages[-1]

        init_time = time.time()
        timeout_threshold = synapse.timeout

        token_streamer = partial(
            _forward,
            self,
            prompt,
            init_time,
            timeout_threshold,
        )

        return synapse.create_streaming_response(token_streamer)


def main():
    with HuggingFaceMiner() as miner:
        while True:
            miner.log_status()
            time.sleep(5)

            if miner.should_exit:
                bt.logging.warning("Ending miner...")
                break


if __name__ == "__main__":
    main()

import time
import torch
import argparse
import bittensor as bt

# Bittensor Miner Template:
import einstein
from einstein.protocol import CoreSynapse
from einstein.llms.hf import load_hf_pipeline, HuggingFaceLLM, HuggingFacePipeline
from einstein.llms.hf import HuggingFaceLLM

# import base miner class which takes care of most of the boilerplate
from neurons.miner import Miner

# extract message
import urllib.parse

class ZephyrMiner(Miner):
    """
    Base miner which runs Zephyr (https://huggingface.co/HuggingFaceH4/zephyr-7b-beta)    
    This requires a GPU with at least 20GB of memory.
    To run this miner from the project root directory:
    
    pm2 start neurons/miners/zephyr/miner.py \
    --name "s3_zephyr" \
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
    --wandb.entity sn3 \
    --wandb.project_name miners_experiments
    """

    @classmethod
    def add_args(cls, parser: argparse.ArgumentParser):
        """
        Adds arguments to the command line parser.
        """
        super().add_args(parser)

    def __init__(self, config=None):
        super().__init__(config=config)

        model_kwargs = None
        if self.config.neuron.load_quantized:
            bt.logging.info("Loading quantized model...")
            model_kwargs = dict(
                torch_dtype=torch.float16,
                load_in_8bit=True,
            )

        if self.config.wandb.on:
            self.identity_tags = ("Zephyr_miner",)

            if self.config.neuron.load_quantized:
                self.identity_tags += ("8bits_quantization",)

        self.llm_pipeline = HuggingFacePipeline(
            model_id=self.config.neuron.model_id,
            torch_dtype=torch.float16,
            device=self.device,
            mock=self.config.mock,
            model_kwargs=model_kwargs,
        )

        self.system_prompt = """
        You are an advanced Math AI Solver. Your task is to provide users with clear and concise explanations 
        and answers to their math questions.
        After the generation you must end the generation with 'The final answer is: {the answer}'.

Template:
Example_1 = [
    {"role": "user", "content": "How do I solve for x in the equation 2x + 3 = 7?"},
    {"role": "assistant", "content": "To solve for x in the equation 2x + 3 = 7, we first subtract 3 from both sides of the equation to get 2x = 4. Then, we divide both sides by 2 to find x = 2. The final answer is: 2"}
]

Example_2 = [
    {"role": "user", "content": "What is the area of a circle with a radius of 4cm?"},
    {"role": "assistant", "content": "The area of a circle is calculated using the formula A = πr^2, where A is the area and r is the radius of the circle. Plugging in a radius of 4cm, the calculation is A = π(4)^2 = 16π cm^2. The final answer is: 16π"}
]

Example_3 = [
    {"role": "user", "content": "If I have a rectangle with a length of 8cm and a width of 3cm, what is its perimeter?"},
    {"role": "assistant", "content": "The perimeter of a rectangle can be found using the formula P = 2(l + w), where P is the perimeter, l is the length, and w is the width. For a rectangle with a length of 8cm and a width of 3cm, the calculation is P = 2(8 + 3) = 2(11) = 22cm. The final answer is: 22cm"}
]
        """
        
        bt.logging.info(f"🧠 Zephyr current system prompt: {self.system_prompt}")

    async def forward(self, synapse: CoreSynapse) -> CoreSynapse:
        """
        Processes the incoming synapse by performing a predefined operation on the input data.
        This method should be replaced with actual logic relevant to the miner's purpose.

        Args:
            synapse (CoreSynapse): The synapse object containing the 'dummy_input' data.

        Returns:
            CoreSynapse: The synapse object with the 'dummy_output' field set to twice the 'dummy_input' value.

        The 'forward' function is a placeholder and should be overridden with logic that is appropriate for
        the miner's intended operation. This method demonstrates a basic transformation of input data.
        """

        try:
            t0 = time.time()
            bt.logging.debug(f"📧 Message received, forwarding synapse: {synapse}")

            # Get the math question from the last message
            role = synapse.roles[-1]
            raw_message = synapse.messages[-1]
            message = urllib.parse.parse_qs(raw_message)
            math_question = message.get("question_text", [''])[0]
            message_type = message.get("question_type", [''])[0]

            prompt = math_question
            bt.logging.debug(f"💬 Querying Zephyr: {prompt}")

            response = HuggingFaceLLM(
                llm_pipeline=self.llm_pipeline,
                system_prompt=self.system_prompt,
                max_new_tokens=self.config.neuron.max_tokens,
                do_sample=self.config.neuron.do_sample,
            ).query(
                message=prompt,  # For now we just take the last message
                role="user",
                disregard_system_prompt=False,
            )

            synapse.completion = response
            synapse_latency = time.time() - t0

            if self.config.wandb.on:
                # TODO: Add system prompt to wandb config and not on every step
                self.log_event(
                    timing=synapse_latency,
                    prompt=prompt,
                    completion=response,
                    system_prompt=self.system_prompt,
                )

            bt.logging.debug(f"✅ Served Response: {response}")
            torch.cuda.empty_cache()
            self.step += 1

        except Exception as e:
            bt.logging.error(f"Error: {e}")
            synapse.completion = "Error: " + str(e)
        finally:
            if self.config.neuron.stop_on_forward_exception:
                self.should_exit = True
            return synapse


# This is the main function, which runs the miner.
if __name__ == "__main__":
    with ZephyrMiner() as miner:
        while True:
            miner.log_status()
            time.sleep(5)

            if miner.should_exit:
                bt.logging.warning("Ending miner...")
                break

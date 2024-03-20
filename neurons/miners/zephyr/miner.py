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
    --neuron.temperature 0.9 \
    --neuron.top_k 50 \
    --neuron.top_p 0.95 \
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
        Mandatory:
        - If the answer is a symbol, you must say 'So the final answer is: (that symbol)'.
        - Unless not symbol, you always end the entire sentence with 'So the final answer is: (the answer)'
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

            prompt = synapse.messages[-1]
            bt.logging.debug(f"💬 Querying Zephyr: {prompt}")

            response = HuggingFaceLLM(
                llm_pipeline=self.llm_pipeline,
                system_prompt=self.system_prompt,
                max_new_tokens=self.config.neuron.max_tokens,
                do_sample=self.config.neuron.do_sample,
                temperature=self.config.neuron.temperature,
                top_k=self.config.neuron.top_k,
                top_p=self.config.neuron.top_p,
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

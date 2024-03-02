import time
import torch
import argparse
import bittensor as bt

from neurons.miner import Miner
from einstein.protocol import CoreSynapse
from einstein.llm import load_pipeline
from einstein.llm import HuggingFaceLLM

class ZephyrMiner(Miner):
    @classmethod
    def add_args(cls, parser: argparse.ArgumentParser):
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
            self.identity_tags = ("zephyr_miner",)

            if self.config.neuron.load_quantized:
                self.identity_tags += ("8bits_quantization",)

        self.llm_pipeline = load_pipeline(
            # model_id=self.config.neuron.model_id,
            model_id='HuggingFaceH4/zephyr-7b-beta',
            torch_dtype=torch.float16,
            device=self.device,
            mock=self.config.mock,
            model_kwargs=model_kwargs,
        )
        self.system_prompt = self.config.neuron.system_prompt

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
            bt.logging.debug(f"💬 Querying zephyr: {prompt}")
            response = (HuggingFaceLLM(
                llm_pipeline=self.llm_pipeline,
                system_prompt=self.system_prompt,
                max_new_tokens=self.config.neuron.max_tokens, # default :256
                do_sample=self.config.neuron.do_sample,
                temperature=self.config.neuron.temperature,# default :0.7 ( the higher the more randomness and creativity )
                top_k=self.config.neuron.top_k,# default :50 
                top_p=self.config.neuron.top_p,# default :0.95
            ).
            queryTemp(
                message=synapse.messages[-1],
                # disregard_system_prompt=False,
                # cleaner=None,
            ))
            synapse.completion = response
            synapse_latency = time.time() - t0

            if self.config.wandb.on:
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
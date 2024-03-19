import time
import torch
import argparse
import bittensor as bt

from neurons.miner import Miner
from einstein.protocol import CoreSynapse
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from NumPAL import NumPAL

import warnings

warnings.filterwarnings("ignore")

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
                max_new_tokens=self.config.neuron.max_tokens,
                temperature=self.config.neuron.temperature,
                torch_dtype=torch.float16,
                top_k=self.config.neuron.top_k,# default :50
                top_p=self.config.neuron.top_p,# default :0.95
                load_in_8bit=True,
                )

        if not self.config.numpal.off:
            bt.logging.info("⚡️ \033[1;33mSupercharging the model with NumPAL...\033[0m")
        else:
            bt.logging.info(f"NumPAL is turned off...")
        if not self.config.numpal.verbose.off:
            bt.logging.info(f"NumPAL verbose mode is turned on...")
        else:
            bt.logging.info(f"NumPAL verbose mode is turned off...")

        if self.config.wandb.on:
            self.identity_tags = ("zephyr_miner",)

            if self.config.neuron.load_quantized:
                self.identity_tags += ("8bits_quantization",)
        
        model_id = "HuggingFaceH4/zephyr-7b-beta"
        self.llm_pipeline = HuggingFacePipeline.from_model_id(
            model_id=model_id,
            task="text-generation",
            pipeline_kwargs=model_kwargs,
            device=0
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

            question = synapse.messages[-1]
            
            if not self.config.numpal.off:

                bt.logging.debug("\033[1;32m💬 Running Math Code on NumPAL\033[0m")
                verbose_on = not self.config.numpal.verbose.off
                pal = NumPAL.from_math_prompt(self.llm_pipeline, verbose=verbose_on)
                q_r = pal.invoke(question)
                # Save the result from NumPAL to self.pal_result
                synapse.pal_result = q_r['result']
                prompt = """
                You are an advanced Math AI Solver. Your task is to provide users with clear and concise explanations and answers to their math questions. When a question is presented to you, utilize the provided reference question and result to generate an insightful concise explanation and the correct answer. If the reference lacks a result or contains an error, independently calculate the answer based on the question given in the reference. Your goal is to ensure the user not only receives the correct answer but also understands the underlying mathematical concepts and processes involved.
                When ever you finish your response, you always end the entire sentence with 'So the final answer is: {the answer}'
                If the answer is a symbol, you must say 'So the final answer is: {that symbol}'.
                """
                
                messages = [
                    SystemMessage(
                        content=prompt
                        ),
                    HumanMessage(
                        content=str(q_r)
                        ),
                    ]

                response = self.llm_pipeline.invoke(messages)
                
            else:
                prompt = ChatPromptTemplate.from_messages(
                    [("system", self.system_prompt), ("user", "{input}")]
                )
                chain = prompt | self.llm_pipeline | StrOutputParser()

                role = synapse.roles[-1]
                message = synapse.messages[-1]

                bt.logging.debug(f"💬 Querying: {prompt}")
                synapse.pal_result=None
                response = chain.invoke({"role": role, "input": message})

            synapse.completion = response
            synapse_latency = time.time() - t0

            if self.config.wandb.on and not self.config.numpal.on:
                self.log_event(
                    timing=synapse_latency,
                    prompt=message,
                    completion=response,
                    system_prompt=self.system_prompt
                )

            if self.config.wandb.on and self.config.numpal.on:
                self.log_event(
                    timing=synapse_latency,
                    prompt=message,
                    completion=response,
                    system_prompt=prompt,
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
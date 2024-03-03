import os
import time
import bittensor as bt
import argparse

# Bittensor Miner Template:
import einstein
from einstein.protocol import CoreSynapse

# import base miner class which takes care of most of the boilerplate
from neurons.miner import Miner

from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.callbacks import get_openai_callback
from dotenv import load_dotenv, find_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import SystemMessage, HumanMessage

# Supercharger:
from neurons.miners.tools.num_pal.base import NumPAL
import dotenv

dotenv.load_dotenv()


import warnings

warnings.filterwarnings("ignore")


class OpenAIMiner(Miner):
    """Langchain-based miner which uses OpenAI's API as the LLM.

    You should also install the dependencies for this miner, which can be found in the requirements.txt file in this directory.
    """

    @classmethod
    def add_args(cls, parser: argparse.ArgumentParser):
        """
        Adds OpenAI-specific arguments to the command line parser.
        """
        super().add_args(parser)

    def __init__(self, config=None):
        super().__init__(config=config)

        bt.logging.info(f"Initializing with model {self.config.neuron.model_id}...")

        if self.config.wandb.on:
            self.identity_tags = ("openai_miner",) + (self.config.neuron.model_id,)

        _ = load_dotenv(find_dotenv())
        api_key = os.environ.get("OPENAI_API_KEY")

        # Set openai key and other args
        self.model = ChatOpenAI(
            api_key=api_key,
            model_name=self.config.neuron.model_id,
            max_tokens=self.config.neuron.max_tokens,
            temperature=self.config.neuron.temperature,
        )
        
        
        self.accumulated_total_tokens = 0
        self.accumulated_prompt_tokens = 0
        self.accumulated_completion_tokens = 0
        self.accumulated_total_cost = 0

    def get_cost_logging(self, cb):
        bt.logging.info(f"Total Tokens: {cb.total_tokens}")
        bt.logging.info(f"Prompt Tokens: {cb.prompt_tokens}")
        bt.logging.info(f"Completion Tokens: {cb.completion_tokens}")
        bt.logging.info(f"Total Cost (USD): ${round(cb.total_cost,4)}")

        self.accumulated_total_tokens += cb.total_tokens
        self.accumulated_prompt_tokens += cb.prompt_tokens
        self.accumulated_completion_tokens += cb.completion_tokens
        self.accumulated_total_cost += cb.total_cost

        return {
            "total_tokens": cb.total_tokens,
            "prompt_tokens": cb.prompt_tokens,
            "completion_tokens": cb.completion_tokens,
            "total_cost": cb.total_cost,
            "accumulated_total_tokens": self.accumulated_total_tokens,
            "accumulated_prompt_tokens": self.accumulated_prompt_tokens,
            "accumulated_completion_tokens": self.accumulated_completion_tokens,
            "accumulated_total_cost": self.accumulated_total_cost,
        }

    async def forward(self, synapse: CoreSynapse) -> CoreSynapse:
        try:
            with get_openai_callback() as cb:
                t0 = time.time()
                bt.logging.debug(f"📧 Message received, forwarding synapse: {synapse}")

                math_question = synapse.messages[-1]

                # Initialize NumPAL and solve the math problem
                bt.logging.debug("\033[1;32m💬 Running Math Code on NumPAL\033[0m")
                pal = NumPAL.from_math_prompt(self.model, verbose=self.config.neuron.numpal_verbose)
                q_r = pal.invoke(math_question)

                # Prepare messages for generating an explanation
                prompt = "You are an advanced Math AI Solver. Your task is to provide users with clear and concise explanations and answers to their math questions. When a question is presented to you, utilize the provided reference question and result to generate an insightful concise explanation and the correct answer. If the reference lacks a result or contains an error, independently calculate the answer based on the question given in the reference. Your goal is to ensure the user not only receives the correct answer but also understands the underlying mathematical concepts and processes involved."
                
                messages = [
                    SystemMessage(
                        content=prompt
                    ),
                    HumanMessage(
                        content=str(q_r)
                    ),
                ]

                # Use another instance of ChatOpenAI if needed, or adjust according to your setup
                response_content = self.model.invoke(messages).content

                synapse.completion = response_content
                synapse_latency = time.time() - t0

                if self.config.wandb.on:
                    self.log_event(
                        timing=synapse_latency,
                        prompt=math_question,
                        completion=response_content,
                        system_prompt=prompt,
                        extra_info=self.get_cost_logging(cb),
                    )

            bt.logging.debug(f"\033[1;32m✅ Served Response: \033[0m {response_content}")
            self.step += 1

            return synapse
        except Exception as e:
            bt.logging.error(f"Error in forward: {e}")
            synapse.completion = "Error: " + str(e)
        finally:
            if self.config.neuron.stop_on_forward_exception:
                self.should_exit = True
            return synapse


# This is the main function, which runs the miner.
if __name__ == "__main__":
    with OpenAIMiner() as miner:
        while True:
            miner.log_status()
            time.sleep(5)

            if miner.should_exit:
                bt.logging.warning("Ending miner...")
                break

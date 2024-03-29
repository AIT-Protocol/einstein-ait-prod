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
from NumPAL import NumPAL
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
        
        if not self.config.numpal.off:
            bt.logging.info("⚡️ \033[1;33mSupercharging the model with NumPAL...\033[0m")
        else:
            bt.logging.info(f"NumPAL is turned off...")
        
        if not self.config.numpal.verbose.off:
            bt.logging.info(f"NumPAL verbose mode is turned on...")
        else:
            bt.logging.info(f"NumPAL verbose mode is turned off...")
        
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
        
        system_prompt = self.config.neuron.system_prompt
        self.system_prompt = system_prompt + """\nMandatory:
        - If the answer is a symbol, you must say 'So the final answer is: (that symbol)'.
        - Unless not symbol, you always end the entire sentence with 'So the final answer is: (the answer)'
        """
        
        bt.logging.info(f'Your current system prompt is: {self.system_prompt}')
        
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
            # with get_openai_callback() as cb:
            t0 = time.time()
            bt.logging.debug(f"📧 Message received, forwarding synapse: {synapse}")
            
            # Create a chain of operations to process the input
            prompt = ChatPromptTemplate.from_messages(
                [("system", self.system_prompt), ("user", "{input}")]
                )
            
            chain = prompt | self.model | StrOutputParser()
            
            role = synapse.roles[-1]
            
            # Get the math question from the last message
            math_question = synapse.messages[-1]
            
            # If NumPAL is turned on, use it to process the math question
            if not self.config.numpal.off:

                bt.logging.debug("\033[1;32m💬 Running Math script on NumPAL\033[0m")
                verbose_on = not self.config.numpal.verbose.off
                
                q_r = NumPAL.from_math_prompt(self.model, verbose=verbose_on).invoke(math_question)
                
                response = chain.invoke({"role": role, "input": str(q_r)})

            # If NumPAL is turned off, use the model to process the math question
            else:

                bt.logging.debug(f"💬 Querying OpenAI...")

                response = chain.invoke({"role": role, "input": math_question})

            synapse.completion = response
            synapse_latency = time.time() - t0
            
            bt.logging.info(f'📧 \033[1;34mMessage received: {math_question}\033[0m')
            bt.logging.info(f'📧 \033[1;34mResponse: {response}\033[0m')

            if self.config.wandb.on:
                self.log_event(
                    timing=synapse_latency,
                    prompt=math_question,
                    completion=response,
                    system_prompt=self.system_prompt,
                    # extra_info=self.get_cost_logging(cb),
                )

            bt.logging.debug(f"✅ \033[1;32mResponse Served: \033[0m {synapse}")
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

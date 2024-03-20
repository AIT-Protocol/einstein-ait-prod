import time
import torch
import bittensor as bt

from einstein.forward import forward
from einstein.llms import HuggingFacePipeline, vLLMPipeline
from einstein.base.validator import BaseValidatorNeuron
from einstein.rewards import RewardPipeline


class Validator(BaseValidatorNeuron):

    def __init__(self, config=None):
        super(Validator, self).__init__(config=config)

        bt.logging.info("load_state()")
        self.load_state()        
        
        self.llm_pipeline = vLLMPipeline(
            model_id=self.config.neuron.model_id,
            device=self.device,
            mock=self.config.mock,
        )

        if sum(self.config.neuron.task_p) != 1:
            raise ValueError("Task probabilities do not sum to 1.")

        # Filter out tasks with 0 probability
        self.active_tasks = [
            task
            for task, p in zip(self.config.neuron.tasks, self.config.neuron.task_p)
            if p > 0
        ]
        # Load the reward pipeline
        self.reward_pipeline = RewardPipeline(
            selected_tasks=self.active_tasks, device=self.device
        )

    async def forward(self):
        """
        Validator forward pass. Consists of:
        - Generating the query
        - Querying the miners
        - Getting the responses
        - Rewarding the miners
        - Updating the scores
        """
        return await forward(self)

    def __enter__(self):

        if self.config.no_background_thread:
            bt.logging.warning("Running validator in main thread.")
            self.run()
        else:
            self.run_in_background_thread()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Stops the validator's background operations upon exiting the context.
        This method facilitates the use of the validator in a 'with' statement.

        Args:
            exc_type: The type of the exception that caused the context to be exited.
                      None if the context was exited without an exception.
            exc_value: The instance of the exception that caused the context to be exited.
                       None if the context was exited without an exception.
            traceback: A traceback object encoding the stack trace.
                       None if the context was exited without an exception.
        """
        if self.is_running:
            bt.logging.debug("Stopping validator in background thread.")
            self.should_exit = True
            self.thread.join(5)
            self.is_running = False
            bt.logging.debug("Stopped")


# The main function parses the configuration and runs the validator.
if __name__ == "__main__":
    with Validator() as v:
        while True:
            bt.logging.info(
                f"Validator running:: network: {v.subtensor.network} | block: {v.block} | step: {v.step} | uid: {v.uid} | last updated: {v.block-v.metagraph.last_update[v.uid]} | vtrust: {v.metagraph.validator_trust[v.uid]:.3f} | emission {v.metagraph.emission[v.uid]:.3f}"
            )
            time.sleep(5)

            if v.should_exit:
                bt.logging.warning("Ending validator...")
                break

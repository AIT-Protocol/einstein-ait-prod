import time
import sys
import numpy as np
import bittensor as bt
from time import sleep

from typing import List
from einstein.agent import HumanAgent
from einstein.dendrite import DendriteResponseEvent
from einstein.conversation import create_task
from einstein.protocol import CoreSynapse
from einstein.rewards import RewardResult
from einstein.utils.uids import get_random_uids
from einstein.utils.logging import log_event


async def run_step(
    self, agent: HumanAgent, k: int, timeout: float, exclude: list = None
):
    """Executes a single step of the agent, which consists of:
    - Getting a list of uids to query
    - Querying the network
    - Rewarding the network
    - Updating the scores
    - Logging the event

    Args:
        agent (HumanAgent): The agent to run the step for.
        k (int): The number of uids to query.
        timeout (float): The timeout for the queries.
        exclude (list, optional): The list of uids to exclude from the query. Defaults to [].
    """

    bt.logging.debug("run_step", agent.task.name)

    # Record event start time.
    start_time = time.time()
    # Get the list of uids to query for this step.
    uids = get_random_uids(self, k=k, exclude=exclude or []).to(self.device)

    axons = [self.metagraph.axons[uid] for uid in uids]
    # Make calls to the network with the prompt.
    responses: List[CoreSynapse] = await self.dendrite(
        axons=axons,
        synapse=CoreSynapse(roles=["user"], messages=[agent.challenge]),
        timeout=timeout,
    )

    # Encapsulate the responses in a response event (dataclass)
    response_event = DendriteResponseEvent(responses, uids)

    bt.logging.info(f"Created DendriteResponseEvent:\n {response_event}")
    # Reward the responses and get the reward result (dataclass)
    # This contains a list of RewardEvents but can be exported as a dict (column-wise) for logging etc
    reward_result = RewardResult(
        self.reward_pipeline,
        agent=agent,
        response_event=response_event,
        device=self.device,
    )
    bt.logging.info(f"Created RewardResult:\n {reward_result}")

    # The original idea was that the agent is 'satisfied' when it gets a good enough response (e.g. reward critera is met, such as AdvancedMath>threshold)
    if reward_result.rewards.numel() > 0:
        top_reward = reward_result.rewards.max()
        top_response = response_event.completions[reward_result.rewards.argmax()]
    else:
        # Provide default values for top_reward and top_response in case of empty tensor
        top_reward = 0  # Default value, adjust as needed
        top_response = ""  # Assuming an empty string as a default, adjust based on what makes sense for your application

    agent.update_progress(
        top_reward=top_reward,
        top_response=top_response,
        )

    self.update_scores(reward_result.rewards, uids)

    # Log the step event.
    event = {
        "block": self.block,
        "step_time": time.time() - start_time,
        **agent.__state_dict__(full=self.config.neuron.log_full),
        **reward_result.__state_dict__(full=self.config.neuron.log_full),
        **response_event.__state_dict__(),
    }

    log_event(self, event)

    return event


async def forward(self):
    bt.logging.info("🚀 Starting forward loop...")

    while True:
        bt.logging.info(
            f"📋 Selecting task... from {self.config.neuron.tasks} with distribution {self.config.neuron.task_p}"
        )
        bt.logging.info(
            f"Tasks: {self.config.neuron.tasks}, Probabilities: {self.config.neuron.task_p}"
        )

        # Create a specific task
        # task_name = np.random.choice(
        #     self.config.neuron.tasks, p=self.config.neuron.task_p
        # )
        task_name = "math"
        bt.logging.info(f"\033[1;32;40m📋 Creating {task_name} task...\033[0m")
        try:
            task = create_task(llm_pipeline=self.llm_pipeline, task_name=task_name)
            break
        except Exception as e:
            bt.logging.error(
                f"\033[1;31;40mFailed to create {task_name} task. {sys.exc_info()}. Skipping to next task. \033[0m"
            )
            bt.logging.info(f"Resetting task creation function...")
            sleep(5)
            continue

    # Create random agent with task, topic, profile...
    bt.logging.info(f"\033[1;32;40m🤖 Creating agent for {task_name} task...\033[0m")
    agent = HumanAgent(
        task=task, llm_pipeline=self.llm_pipeline, begin_conversation=True
    )

    rounds = 0
    exclude_uids = []
    while not agent.finished:
        # when run_step is called, the agent updates its progress
        event = await run_step(
            self,
            agent,
            k=self.config.neuron.sample_size,
            timeout=self.config.neuron.timeout,
            exclude=exclude_uids,
        )
        exclude_uids += event["uids"]
        task.complete = True

        rounds += 1

    del agent
    del task

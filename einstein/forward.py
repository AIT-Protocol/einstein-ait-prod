import sys
import time
import random
import asyncio
import traceback
import numpy as np
import bittensor as bt
from typing import List, Dict, Awaitable
from einstein.agent import HumanAgent
from einstein.dendrite import DendriteResponseEvent, SynapseStreamResult
from einstein.conversation import create_task
from einstein.protocol import StreamCoreSynapse, ClientRequestSynapse
from einstein.rewards import RewardResult
from einstein.utils.uids import get_random_uids
from einstein.utils.logging import log_event
from einstein.utils.misc import async_log, serialize_exception_to_string
from transformers import PreTrainedTokenizerFast as Tokenizer
from einstein.utils.uids import get_random_uids
from dataclasses import dataclass
import urllib.parse

SINGLE_TURN_TASKS = ['sentiment', 'translation']

@async_log
async def generate_reference(agent):
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, agent.task.generate_reference, agent.llm_pipeline)
    return result

@async_log
async def execute_dendrite_call(dendrite_call):
    responses = await dendrite_call
    return responses


async def process_stream(uid: int, async_iterator: Awaitable, tokenizer: Tokenizer) -> SynapseStreamResult:
    """Process a single response asynchronously."""
    synapse = None  # Initialize chunk with a default value
    exception = None
    accumulated_chunks = []
    accumulated_chunks_timings = []
    accumulated_tokens_per_chunk = []
    start_time = time.time()
    
    try:                
        async for chunk in async_iterator:  # most important loop, as this is where we acquire the final synapse.
            if isinstance(chunk, str):
                accumulated_chunks.append(chunk)
                accumulated_chunks_timings.append(time.time() - start_time)
                
                tokens_in_chunk = len(tokenizer.tokenize(chunk))
                accumulated_tokens_per_chunk.append(tokens_in_chunk)
                
                bt.logging.debug(f"\nchunk for uid {uid}: {chunk}")

        # Assuming last chunk of async_iterator holds the last value yielded as a StreamingSynapse
        synapse = chunk
        if synapse is None or not isinstance(synapse, StreamCoreSynapse):
            raise ValueError(
                f"Something went wrong with miner uid {uid}, Synapse is not StreamCoreSynapse."
            )
    except Exception as e:        
        exception = e
        traceback_details = traceback.format_exc()
        bt.logging.error(
            f"Error in generating reference or handling responses for uid {uid}: {e}\n{traceback_details}"
        )

        failed_synapse = StreamCoreSynapse(
            roles=["user"], messages=["failure"], completion=""
        )

        synapse = failed_synapse
    finally:
        return SynapseStreamResult(
            accumulated_chunks=accumulated_chunks,
            accumulated_chunks_timings=accumulated_chunks_timings,
            tokens_per_chunk=accumulated_tokens_per_chunk,
            synapse=synapse,
            uid=uid,
            exception=exception
        )


@async_log
async def handle_response(stream_results_dict: Dict[int, Awaitable], tokenizer: Tokenizer) -> List[SynapseStreamResult]:
    """The handle_response function is responsible for creating asyncio tasks around acquiring streamed miner chunks
    and processing them asynchronously. It then pairs the results with their original UIDs and returns a list of StreamResults.

    Args:
        responses (Dict[int, Awaitable]): Responses contains awaitables that are used to acquire streamed miner chunks.

    Raises:
        ValueError

    Returns:
        List[StreamResult]: DataClass containing the synapse, exception, and uid
    """
    tasks_with_uid = [
        (uid, stream_results_dict[uid]) for uid, _ in stream_results_dict.items()
    ]  # Pair UIDs with their tasks

    # Start tasks, preserving order and their associated UIDs
    process_stream_tasks = [process_stream(uid, resp, tokenizer) for uid, resp in tasks_with_uid]
    processed_stream_results = await asyncio.gather(*process_stream_tasks, return_exceptions=True) 
    
    return processed_stream_results


@async_log
async def generate_reference(agent: HumanAgent):
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None, agent.task.generate_reference, agent.llm_pipeline
    )
    return result


def log_stream_results(stream_results: List[SynapseStreamResult]):
    failed_responses = [
        response for response in stream_results if response.exception is not None
    ]
    empty_responses = [
        response
        for response in stream_results
        if response.exception is None and response.synapse.completion == ""
    ]
    non_empty_responses = [
        response
        for response in stream_results
        if response.exception is None and response.synapse.completion != ""
    ]

    bt.logging.info(f"Total of non_empty responses: ({len(non_empty_responses)})")
    bt.logging.info(f"Total of empty responses: ({len(empty_responses)})")
    bt.logging.info(
        f"Total of failed responses: ({len(failed_responses)}):\n {failed_responses}"
    )

    for failed_response in failed_responses:
        formatted_exception = serialize_exception_to_string(failed_response.exception)
        bt.logging.error(
            f"Failed response for uid {failed_response.uid}: {formatted_exception}"
        )


async def run_step(
    self, agent: HumanAgent, roles: List[str], messages: List[str], k: int, timeout: float, exclude: list = None
):
    """Executes a single step of the agent, which consists of:
    - Getting a list of uids to query
    - Querying the network
    - Rewarding the network
    - Updating the scores
    - Logging the event

    Args:
        agent (HumanAgent): The agent to run the step for.
        roles (List[str]): The roles for the synapse.
        messages (List[str]): The messages for the synapse.
        k (int): The number of uids to query.
        timeout (float): The timeout for the queries.
        exclude (list, optional): The list of uids to exclude from the query. Defaults to [].
    """
    bt.logging.debug("run_step", agent.task.name)

    # Record event start time.
    start_time = time.time()
    # Get the list of uids to query for this step.
    uids = get_random_uids(self, k=k, exclude=exclude or []).to(self.device)
    uids_cpu = uids.cpu().tolist()

    axons = [self.metagraph.axons[uid] for uid in uids]
    bt.logging.debug(f"axons: {axons}")

    # Directly call dendrite and process responses in parallel
    streams_responses = await self.dendrite(
        axons=axons,
        synapse=StreamCoreSynapse(roles=roles, messages=messages),
        timeout=timeout,
        deserialize=False,
        streaming=True,
    )

    # Prepare the task for handling stream responses
    stream_results_dict = dict(zip(uids_cpu, streams_responses))
    tokenizer = self.llm_pipeline.tokenizer
    handle_stream_responses_task = asyncio.create_task(handle_response(stream_results_dict, tokenizer))

    if not agent.task.static_reference:
        reference_generation_task = generate_reference(agent)
        _, stream_results = await asyncio.gather(
            reference_generation_task, handle_stream_responses_task
        )
    else:
        stream_results = await handle_stream_responses_task

    log_stream_results(stream_results)

    # Encapsulate the responses in a response event (dataclass)
    response_event = DendriteResponseEvent(
        stream_results=stream_results, uids=uids, timeout=timeout
    )

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

    best_response = response_event.completions[reward_result.rewards.argmax()]

    # The original idea was that the agent is 'satisfied' when it gets a good enough response (e.g. reward critera is met, such as ROUGE>threshold)
    agent.update_progress(
        top_reward=reward_result.rewards.max(),
        top_response=best_response,
    )

    self.update_scores(reward_result.rewards, uids)
    
    # Log the step event.
    event = {
        "best": best_response,
        "block": self.block,
        "step": self.step,
        "step_time": time.time() - start_time,        
        **agent.__state_dict__(full=self.config.neuron.log_full),
        **reward_result.__state_dict__(full=self.config.neuron.log_full),
        **response_event.__state_dict__(),
    }
    
    top_response = best_response
    
    return event, top_response


async def forward(self):
    """
    Encapsulates a full conversation between the validator and miners. Contains one or more rounds of request-response.

    """
    bt.logging.info("🚀 Starting forward loop...")
    forward_start_time = time.time()
    

    while True:
        # get data in queue
        try:
            synapse = self.api_queue.get_nowait()
            _message = urllib.parse.parse_qs(synapse.input_synapse.messages[0])
            _problem = _message.get('question_text', [''])[0]
            bt.logging.info(f"📡 Received synapse: {synapse}")
        except:
            synapse = None
            _problem = ''
            bt.logging.info(f"🤖 Generate problem")
            pass
        
        # Create a specific task
        # task_name = np.random.choice(
        #     self.config.neuron.tasks, p=self.config.neuron.task_p
        # )
        task_name = "math"
        bt.logging.info(f"📋 Creating {task_name} task... ")
        try:
            task = create_task(
                llm_pipeline=self.llm_pipeline,
                translation_pipeline=self.translation_pipeline,
                task_name=task_name,
                create_reference=False,
                problem=_problem
            )
            break
        except Exception as e:
            bt.logging.error(
                f"Failed to create {task_name} task. {sys.exc_info()}. Skipping to next task."
            )
            if synapse: synapse.event.set()
            continue

    # Create random agent with task, topic, profile...
    bt.logging.info(f"🤖 Creating agent for {task_name} task... ")
    agent = HumanAgent(
        task=task, llm_pipeline=self.llm_pipeline, begin_conversation=True
    )

    turn = 0
    exclude_uids = []
    
    # convert challenge into miner's message format
    agent.challenge = urllib.parse.urlencode({
        "question_text": agent.challenge,
        "question_markdown": "",
        "question_type": ""
    })
    
    roles = ['user']
    messages = [agent.challenge]
    while True:
        # Note: The try catch is a safe clause to ensure that the forward loop continues even if an error occurs in run_step.
        # To be reconsidered in the next version.
        try:
            # when run_step is called, the agent updates its progress
            event, top_response = await run_step(
                self,
                agent,
                roles=roles,
                messages=messages,
                k=self.config.neuron.sample_size,
                timeout=self.config.neuron.timeout,
                exclude=exclude_uids,
            )
            if synapse:
                synapse.output_synapse = StreamCoreSynapse(
                    roles=["validator"], messages=[top_response], completion=top_response
                )
                synapse.event.set()
                self.api_queue.task_done()

            # Adds forward time to event and logs it to wandb
            event["forward_time"] = time.time() - forward_start_time
            event["turn"] = turn
            log_event(self, event)
            task.complete = True
            
            accepted_answer = event["best"] if random.random() < 0.5 else agent.task.reference
            roles.append("assistant")
            messages.append(accepted_answer)

            # 50% chance of single turn conversation, 25% of two turns, 12.5% chance of 3 turns, 6.25% chance of 4 turns, 3.63% chance of 5...
            if random.random()<0.5 or turn>=1:
                break

            if task.name in SINGLE_TURN_TASKS:
                break

            history = '\n'.join([f"{role}: {message}" for role, message in zip(roles, messages)])

            # overwrite the challenge with the followup query, which *should* continue the persona
            agent.challenge = agent.task.query

            roles.append("user")
            messages.append(agent.challenge)
            turn += 1

        except BaseException as e:
            unexpected_errors = serialize_exception_to_string(e)
            bt.logging.error(
                f"Error in run_step: Skipping to next round. \n {unexpected_errors}"
            )

            event = {"unexpected_errors": unexpected_errors}

            log_event(self, event)
            continue

    del agent
    del task
    if not synapse:
        # Make sure that the miner finishes the process of the current request and returns a response
        # Otherwise, there is a case where the validator sends a new request while the miner is still processing the old one
        # Then, the response of the old request will be applied as the response of the new request
        bt.logging.info("💤 Sleep 5 seconds...")
        time.sleep(5)

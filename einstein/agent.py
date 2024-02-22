import textwrap
import time
import bittensor as bt
from dataclasses import asdict
from einstein.tasks import Task
from einstein.llm import HuggingFaceLLM
from einstein.cleaners.cleaner import CleanerPipeline
from einstein.persona import Persona, create_persona
from transformers import Pipeline

import warnings
warnings.filterwarnings("ignore")


class HumanAgent(HuggingFaceLLM):
    "Agent that impersonates a human user, specifically seeking assistance from Einstein in solving complex mathematical problems."

    @property
    def progress(self):
        return int(self.task.complete)

    @property
    def finished(self):
        return self.progress == 1

    system_prompt_template = textwrap.dedent(
        """This is a roleplaying game where you are impersonating {mood} human user with a specific persona. As a human, you are using AI assistant to {desc} related to {topic} ({subtopic}) in a {tone} tone. You don't need to greet the assistant or be polite, unless this is part of your persona. The spelling and grammar of your messages should also reflect your persona.

        Your singular focus is to use the assistant to {goal}: {query}
    """
    )

    def __init__(
        self,
        task: Task,
        llm_pipeline: Pipeline,
        system_template: str = None,
        persona: Persona = None,
        begin_conversation=True,
    ):
        if persona is None:
            persona = create_persona()

        self.persona = persona
        self.task = task
        self.llm_pipeline = llm_pipeline

        if system_template is not None:
            self.system_prompt_template = system_template

        self.system_prompt = self.system_prompt_template.format(
            mood=self.persona.mood,
            tone=self.persona.tone,
            **self.task.__state_dict__(),  # Adds desc, subject, topic
        )

        super().__init__(
            llm_pipeline=llm_pipeline,
            system_prompt=self.system_prompt,
            max_new_tokens=256,
        )

        if begin_conversation:
            bt.logging.info("🤖 Generating challenge query...")
            # initiates the conversation with the miner
            self.challenge = self.create_challenge()

    
    def create_challenge(self) -> str:
        """Creates the opening question to focus on a mathematical challenge suitable for Einstein's expertise."""
        t0 = time.time()

        cleaner = None
        if hasattr(self.task, 'cleaning_pipeline'):
            cleaner = CleanerPipeline(
                cleaning_pipeline=self.task.cleaning_pipeline
            )

        # Example message: "Derive the formula for..."
        self.challenge = super().query(message="Pose a mathematical problem", cleaner=cleaner)
        self.challenge = self.task.format_challenge(self.challenge, domain="mathematics")
        self.challenge_time = time.time() - t0
        
        bt.logging.info(f"🤖 Challenge created: {self.challenge} in {self.challenge_time:.2f} seconds")
        return self.challenge

    def __state_dict__(self, full=False):
        return {
            "challenge": self.challenge,
            "challenge_time": self.challenge_time,
            **self.task.__state_dict__(full=full),
            **asdict(self.persona),
            "system_prompt": self.system_prompt,
        }

    def __str__(self):
        return self.system_prompt

    def __repr__(self):
        return str(self)

    def continue_conversation(self, miner_response: str):
        # Generates response to miner response
        self.query(miner_response)
        # Updates current prompt with new state of conversation
        # self.prompt = self.get_history_prompt()

    def update_progress(
        self, top_reward: float, top_response: str, continue_conversation=False
    ):
        bt.logging.info(f"📈 Updating progress with reward {top_reward:.2f}...")
        bt.logging.info(f"📝 Top response: {top_response}")
        if top_reward > self.task.reward_threshold:
            self.task.complete = True
            self.messages.append({"content": top_response, "role": "user"})

            bt.logging.info("Agent finished its goal")
            return

        if continue_conversation:
            bt.logging.info(
                "↪ Agent did not finish its goal, continuing conversation..."
            )
            self.continue_conversation(miner_response=top_response)
from typing import List

from prompting.tasks import MathTask
from prompting.rewards import BaseRewardModel
from prompting.rewards.float_diff import FloatDiffModel
from prompting.rewards.advanced_math import AdvancedMathModel

SUPPORTED_TASKS = {
    "math": MathTask
}


REWARD_MODELS = {
    'float_diff': FloatDiffModel,
    'advanced_math': AdvancedMathModel,
}


class RewardPipeline:
    def __init__(self, selected_tasks: List[str], device):
        self.selected_tasks = selected_tasks
        self.device = device
        self.validate_tasks()
        self.load_pipeline()

    def __getitem__(self, __key: str) -> BaseRewardModel:
        return self.reward_models.get(__key)

    def get(self, __key: str) -> BaseRewardModel:
        return self.reward_models.get(__key)

    def __repr__(self):
        return f'RewardPipeline({self.reward_models})'

    def validate_tasks(self):
        
        for task in self.selected_tasks:
            if task not in SUPPORTED_TASKS:
                raise ValueError(
                    f"Task {task} not supported. Please choose from {SUPPORTED_TASKS.keys()}"
                )
            # Check that the reward_definition and penalty_definition are lists of dictionaries whose weights sum to one
            self._check_weights(task, "reward_definition")
            self._check_weights(task, "penalty_definition")

    def _check_weights(self, task, definition):

        total_weight = 0

        model_infos = getattr(SUPPORTED_TASKS[task], definition)
        
        for model_info in model_infos:
            
            if not isinstance(model_info, dict):
                raise ValueError(f"{definition} model {model_info} is not a dictionary.")
            if "weight" not in model_info:
                raise ValueError(f"{definition} model {model_info} does not have a weight.")

            weight = model_info["weight"]
            if not isinstance(weight, (float, int)):
                raise ValueError(f"{definition} model {model_info} weight is not a float.")
            if not 0 <= weight <= 1:
                raise ValueError(f"{definition} model {model_info} weight is not between 0 and 1.")

            total_weight += weight

        if model_infos and total_weight != 1:
            raise ValueError(f"{definition} model {model_infos} weights do not sum to 1 (sum={total_weight})")

    def load_pipeline(self):
        """Dynamically loads the reward models required by the selected tasks so that we only use the necessary resources."""
        active_reward_models = []

        for task in self.selected_tasks:

            active_reward_models += SUPPORTED_TASKS[task].reward_definition
            active_reward_models += SUPPORTED_TASKS[task].penalty_definition

        # Instantiate only the required reward models
        reward_models = {}
        for model in active_reward_models:
            name = model.get("name")
            if not name:
                raise ValueError(f"Reward model {model} does not have a name. ")
            if name not in REWARD_MODELS:
                raise ValueError(
                    f"Reward model {name} not supported. Please choose from {REWARD_MODELS.keys()}"
                )
            elif name in reward_models: # Prevents duplicate reward models
                continue

            cls = REWARD_MODELS[name]

            params = {k: v for k, v in model.items() if k not in ["name", "weight"]}
            reward_models[name] = cls(device=self.device, **params)

        self.reward_models = reward_models


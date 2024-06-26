from typing import List

from einstein.tasks import TASKS

from einstein.rewards import BaseRewardModel
from einstein.rewards.advanced_math import AdvancedMathModel


REWARD_MODELS = {
    'advanced_math': AdvancedMathModel,
}

class RewardPipeline:
    def __init__(self, selected_tasks: List[str], device):
        self.selected_tasks = selected_tasks
        self.device = device
        self.validate_tasks()
        self.load_reward_pipeline()

    def __getitem__(self, __key: str) -> BaseRewardModel:
        return self.reward_models.get(__key)

    def get(self, __key: str) -> BaseRewardModel:
        return self.reward_models.get(__key)

    def __repr__(self):
        return f'RewardPipeline({self.reward_models})'

    def validate_tasks(self):
        for task in self.selected_tasks:
            if task not in TASKS:
                raise ValueError(f"Task {task} not supported. Please choose from {TASKS.keys()}")
            self._check_weights(task, "reward_definition", expected_weight=1)
            self._check_weights(task, "penalty_definition", expected_weight=None)

    def _check_weights(self, task, definition, expected_weight):
        total_weight = 0
        model_infos = getattr(TASKS[task], definition)
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
        if model_infos and expected_weight is not None and total_weight != expected_weight:
            raise ValueError(f"{definition} model {model_infos} weights do not sum to {expected_weight} (sum={total_weight})")

    def load_reward_pipeline(self):
        active_reward_models = []
        for task in self.selected_tasks:
            active_reward_models += TASKS[task].reward_definition
            active_reward_models += TASKS[task].penalty_definition
            active_reward_models += TASKS[task].global_penalty_definition
        reward_models = {}
        for model in active_reward_models:
            name = model.get("name")
            if not name:
                raise ValueError(f"Reward model {model} does not have a name.")
            if name not in REWARD_MODELS:
                raise ValueError(f"Reward model {name} not supported. Please choose from {REWARD_MODELS.keys()}")
            elif name in reward_models:
                continue
            cls = REWARD_MODELS[name]
            params = {k: v for k, v in model.items() if k not in ["name", "weight"]}
            reward_models[name] = cls(device=self.device, **params)
        self.reward_models = reward_models
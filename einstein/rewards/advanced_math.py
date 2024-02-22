import time
import torch
from typing import List
from sympy import simplify, symbols, parse_expr
from einstein.rewards import BaseRewardModel, BatchRewardOutput

class AdvancedMathModel(BaseRewardModel):
    @property
    def name(self) -> str:
        return 'advanced_math'
    
    def __init__(self, **kwargs):
        super().__init__()

    @staticmethod
    def compare_expressions(ref_expr, user_expr):
        # Attempt to parse and simplify both expressions for comparison
        try:
            ref_simplified = simplify(parse_expr(ref_expr))
            user_simplified = simplify(parse_expr(user_expr))
            return ref_simplified.equals(user_simplified)
        except Exception as e:
            print(f"Error parsing expressions: {e}")
            return False

    def math_score(self, reference, completion):
        if self.compare_expressions(reference, completion):
            return 1.0
        else:
            # Further enhancements could include partial scoring based on similarity or closeness of expressions
            return 0.0

    def reward(self, reference: str, completions: List[str]) -> BatchRewardOutput:
        rewards = []
        timings = []

        for completion in completions:
            t0 = time.time()
            reward = self.math_score(reference, completion)
            timings.append(time.time() - t0)
            rewards.append(reward)

        return BatchRewardOutput(
            rewards=torch.FloatTensor(rewards),
            timings=torch.FloatTensor(timings),
            extra_info={'type': 'math'},
        )

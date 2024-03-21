import time
import torch
import re
from typing import List
from sympy.parsing.sympy_parser import parse_expr
from einstein.rewards import BaseRewardModel, BatchRewardOutput, RewardModelTypeEnum


class AdvancedMathModel(BaseRewardModel):
    @property
    def name(self) -> str:
        return "advanced_math"

    def __init__(self, **kwargs):
        super().__init__()

    @staticmethod

    def extract_numeric_values(data):
        """
        Extracts numeric values from a given text.
        
        Args:
            data (str, int, float, or list): The data from which to extract numeric values.
        
        Returns:
            list of float: A list of extracted numeric values.
        """
        if isinstance(data, str):
            numeric_values = re.findall(r"[-+]?\d*\.\d+|\d+", data)
            return [float(value) if '.' in value else int(value) for value in numeric_values]
        elif isinstance(data, int) or isinstance(data, float):
            return [data]
        elif isinstance(data, list):
            extracted_values = []
            for item in data:
                if isinstance(item, str):
                    extracted_values.extend(AdvancedMathModel.extract_numeric_values(item))
                elif isinstance(item, int) or isinstance(item, float):
                    extracted_values.append(item)
            return extracted_values
        else:
            return []
    
    @staticmethod
    def extract_final_answer(text: str):
        """
        Extracts the final answer from a given text based on a specific sentence structure.
        
        Args:
            text (str): The text from which to extract the final answer.
        
        Returns:
            str: The extracted final answer, or None if not found.
        """
        # Regular expression to match the pattern and extract the final answer
        match = re.search(r"the final answer is\:?\s*(.+)", text, re.IGNORECASE)
        if match:
            return match.group(1)
        else:
            return None

    @staticmethod
    def math_score(reference: str, completion: str) -> float:
        """
        Computes a score for answers involving either numeric values or symbols, handling real, complex numbers,
        symbols, and possibly including units, for both single and multiple component answers.
        
        Args:
            reference (str): The reference answer, which may include numeric values, symbols, or units.
            completion_text (str): The text response, used if the NumPAL result is unavailable.
        
        Returns:
            float: A score between 0 and 1 indicating the closeness or match of the completion to the reference.
        """
        extracted_answer = AdvancedMathModel.extract_final_answer(completion)
        if extracted_answer:
            comparison_values = sorted(AdvancedMathModel.extract_numeric_values(extracted_answer))
        else:
            comparison_values = sorted(AdvancedMathModel.extract_numeric_values(completion))

        reference_values = sorted(AdvancedMathModel.extract_numeric_values(reference))

        # Calculate the score for numeric comparisons, ignoring order
        scores = []
        for ref_val, comp_val in zip(reference_values, comparison_values):
            if isinstance(comp_val, (float, int)):
                score = 1 - abs(ref_val - comp_val) / max(abs(ref_val), 1)
                scores.append(max(0, min(score, 1)))
            else:
                return 0.0

        final_score = sum(scores) / len(scores) if scores else 0
        
        return final_score


    def reward(self, reference: str, pal_results: List[str], completions: List[str]) -> BatchRewardOutput:
        """Compute difference scores given a completion and reference pair."""
        rewards = []
        timings = []

        for completion, pal_result in zip(completions, pal_results):
            t0 = time.time()
            reward = self.math_score(reference, pal_result, completion)
            timings.append(time.time() - t0)
            rewards.append(reward)

        output = BatchRewardOutput(
            rewards=torch.FloatTensor(rewards),
            timings=torch.FloatTensor(timings),
            extra_info={
                "type": "math",
            },
        )
        return output

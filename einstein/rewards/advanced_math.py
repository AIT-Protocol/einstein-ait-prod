import time
import torch
import re
# import logging
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
    def extract_numeric_values(text: str):
        """
        Extracts numeric values from a given text.
        
        Args:
            text (str): The text from which to extract numeric values.
        
        Returns:
            list of float: A list of extracted numeric values.
        """
        # Find all numeric values in the text, considering decimal points
        numeric_values = re.findall(r"[-+]?\d*\.\d+|\d+", text)
        return [float(value) for value in numeric_values]
    
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
        match = re.search(r"So the final answer is: (.+)", text)
        if match:
            return match.group(1)  # The part of the regex in parentheses (.+) is the answer
        else:
            return None

    @staticmethod
    def math_score(reference: str, pal_result: str, completion_text: str) -> float:
        """
        Computes a score for answers involving either numeric values or symbols, handling real, complex numbers,
        symbols, and possibly including units, for both single and multiple component answers.
        
        Args:
            reference (str): The reference answer, which may include numeric values, symbols, or units.
            pal_result (str): The direct result from NumPAL, which may be a number, symbol, or tuple.
            completion_text (str): The text response, used if the NumPAL result is unavailable.
        
        Returns:
            float: A score between 0 and 1 indicating the closeness or match of the completion to the reference.
        """
        
        def safe_eval(val):
            try:
                return eval(val)
            except:
                return val
        
        # Direct comparison for symbols
        if reference in ['>', '<', '=', '!=', '≥', '≤'] or pal_result in ['>', '<', '=', '!=', '≥', '≤']:
            return 1.0 if reference == pal_result else 0.0
        
        # Try to evaluate pal_result to handle numeric and complex values
        pal_result_evaluated = safe_eval(pal_result)
        
        # Handle complex numbers and numeric values
        if isinstance(pal_result_evaluated, complex):
            comparison_values = [pal_result_evaluated.real, pal_result_evaluated.imag]
        elif isinstance(pal_result_evaluated, (list, tuple)):
            comparison_values = [safe_eval(val) for val in pal_result_evaluated]
        else:
            extracted_answer = AdvancedMathModel.extract_final_answer(completion_text)
            if extracted_answer:
                comparison_values = AdvancedMathModel.extract_numeric_values(extracted_answer)
            else:
                comparison_values = []
        
        reference_values = AdvancedMathModel.extract_numeric_values(reference)
        
        # Calculate the score for numeric comparisons
        scores = []
        for ref_val, comp_val in zip(reference_values, comparison_values):
            if isinstance(comp_val, float) or isinstance(comp_val, int):
                score = 1 - abs(ref_val - comp_val) / max(abs(ref_val), 1)
                scores.append(max(0, min(score, 1)))  # Ensure score is between 0 and 1
            else:
                return 0.0  # Non-numeric comparison values lead to a score of 0
        
        final_score = sum(scores) / len(scores) if scores else 0
        
        # Before returning the final score, log the intermediate values
        # logging.debug(f"Reference values: {reference_values}")
        # logging.debug(f"Comparison values: {comparison_values}")
        # logging.debug(f"Individual scores: {scores}")
        # logging.debug(f"Final score: {final_score}")
        
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

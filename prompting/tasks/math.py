import sys
import bittensor as bt
from dataclasses import dataclass
from prompting.tasks import Task


@dataclass
class MathTask(Task):
    reward_definition = [
        # Dynamically assign reward models based on problem complexity
        dict(name='float_diff', weight=0.5),
        dict(name='advanced_math', weight=0.5),
    ]
    penalty_definition = []

    def __init__(self, llm_pipeline, context, create_reference=True):
        self.name = "math"
        self.desc = "Solve math problems with varying complexity"
        self.goal = "Find the solution to the math problem"
        self.context = context

        # Handle both numeric and symbolic references
        reference = context["solution"]
        if isinstance(reference, str) and not reference.replace('.', '', 1).isdigit():
            self.reference_type = 'symbolic'
        else:
            self.reference_type = 'numeric'
            try:
                reference = float(reference)
            except ValueError:
                raise ValueError(f"Solution {reference} is not valid.")
        
        self.query = f"How can I solve this math problem: {context['problem']}?"
        self.reference = str(reference)
        self.topic = context["topic"]
        self.subtopic = context["subtopic"]
        self.tags = context.get("tags", [])
        self.static_reference = True
        self.static_query = True



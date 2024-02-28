import sys
import bittensor as bt
from dataclasses import dataclass
from einstein.tasks import Task


@dataclass
class MathTask(Task):
    name = "math"
    desc = "Solve math problems with varying complexity"
    goal = "Find the solution to the math problem"
    
    reward_definition = [
        # Dynamically assign reward models based on problem complexity
        dict(name='float_diff', weight=0.6),
        dict(name='advanced_math', weight=0.4),
    ]
    penalty_definition = []
    
    static_reference = True
    static_query = True


    def __init__(self, llm_pipeline, context, create_reference=True):
        self.context = context
        self.reference = context.extra['solution']

        # Handle both numeric and symbolic references
        if isinstance(self.reference, str) and not self.reference.replace('.', '', 1).isdigit():
            self.reference_type = 'symbolic'
        else:
            self.reference_type = 'numeric'
        
        # Improved concatenation using f-string for better readability and performance
        self.query = "How can I solve the following problem, " + context.content + "? Make sure to include the whole problem when you ask your question."
        self.reference = context.extra['solution']
        self.topic = context.title
        self.subtopic = context.topic
        self.tags = context.tags


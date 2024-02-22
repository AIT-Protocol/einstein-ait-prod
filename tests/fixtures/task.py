from einstein.tasks import Task, MathTask
from .dataset import MATH_CONTEXT

TASKS = [
        MathTask,
    ]

# TODO: Make fully deterministic
CONTEXTS = {
    MathTask:  MATH_CONTEXT
}


from prompting.tasks import (
    Task,
    MathTask,
)
from prompting.tools import (
    MathDataset,
)

from transformers import Pipeline


def create_task(llm_pipeline: Pipeline, task_name: str) -> Task:
    math_based_tasks = ["math"]

    if task_name in math_based_tasks:
        dataset = MathDataset()
        task = MathTask(llm_pipeline=llm_pipeline, context=dataset.next())

    else:
        raise ValueError(f"Task {task_name} not supported. Please choose a valid task")

    return task
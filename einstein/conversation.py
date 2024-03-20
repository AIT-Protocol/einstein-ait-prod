from einstein.tasks import (
    Task,
    MathTask,
)
from einstein.tools import (
    MathDataset
)

from transformers import Pipeline

def create_task(llm_pipeline: Pipeline, task_name: str, problem: str) -> Task:
    math_based_tasks = ["math"]

    if task_name in math_based_tasks:
        dataset = MathDataset()
        task = MathTask(llm_pipeline=llm_pipeline, context=dataset.next())

        # context = Context(
        #     problem=problem,
        #     solution='',
        #     solution_raw='',
        #     topic='',
        #     subtopic='',
        #     fetch_time=0.0
        # )
        
        # task = MathTask(llm_pipeline=llm_pipeline, context=context)

    else:
        raise ValueError(f"Task {task_name} not supported. Please choose a valid task")

    return task
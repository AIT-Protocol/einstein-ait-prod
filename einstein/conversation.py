from einstein.tasks import (
    Task,
    MathTask,
)
from einstein.tools import (
    MathDataset,
)

from .tools.datasets import Context

from transformers import Pipeline


def create_task(llm_pipeline: Pipeline, task_name: str, problem: str) -> Task:
    math_based_tasks = ["math"]

    if task_name in math_based_tasks:
        if not problem:
            dataset = MathDataset()
            task = MathTask(llm_pipeline=llm_pipeline, context=dataset.next())
        else: 
            context = Context(
                title='',
                topic='',
                subtopic='',
                content=problem,
                internal_links=[],
                external_links=[],
                source='',
                tags=[],
                extra={"solution": ''},
                stats={}
            )
            task = MathTask(llm_pipeline=llm_pipeline, context=context)
            
            # generate_reference() function only works if static_reference is False
            _static_ref = task.static_reference
            task.static_reference = False
            task.generate_reference(llm_pipeline, clean=False)
            task.static_reference = _static_ref

    else:
        raise ValueError(f"Task {task_name} not supported. Please choose a valid task")

    return task
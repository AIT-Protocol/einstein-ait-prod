__version__ = "2.0.0"
version_split = __version__.split(".")
__spec_version__ = (
    (10000 * int(version_split[0]))
    + (100 * int(version_split[1]))
    + (1 * int(version_split[2]))
)

# Import all submodules.
from . import protocol
from . import base
from . import rewards
from . import tasks
from . import tools
from . import utils

from . import forward
from . import agent
from . import conversation
from . import dendrite
from . import shared
from . import validator

from .llms import hf

# from .tasks import TASKS
# from .tools import DATASETS
# from .task_registry import TASK_REGISTRY

# # Assert that all tasks have a dataset, and all tasks/datasets are in the TASKS and DATASETS dictionaries.
# registry_missing_task = set(TASKS.keys()) - set(TASK_REGISTRY.keys())
# registry_extra_task = set(TASK_REGISTRY.keys()) - set(TASKS.keys())
# assert (
#     not registry_missing_task
# ), f"Missing tasks in TASK_REGISTRY: {registry_missing_task}"
# assert not registry_extra_task, f"Extra tasks in TASK_REGISTRY: {registry_extra_task}"

# registry_datasets = set(
#     [dataset for task, datasets in TASK_REGISTRY.items() for dataset in datasets]
# )
# registry_missing_dataset = registry_datasets - set(DATASETS.keys())
# registry_extra_dataset = set(DATASETS.keys()) - registry_datasets
# assert (
#     not registry_missing_dataset
# ), f"Missing datasets in TASK_REGISTRY: {registry_missing_dataset}"
# assert (
#     not registry_extra_dataset
# ), f"Extra datasets in TASK_REGISTRY: {registry_extra_dataset}"

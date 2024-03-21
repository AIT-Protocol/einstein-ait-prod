__version__ = "1.2.1"
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
from .llms import hf

import string

# Define the version of the template module.
__version__ = "1.2.1"
__minimal_miner_version__ = "1.2.1"
__minimal_validator_version__ = "1.2.0"

version_split = __version__.split(".")
__version_as_int__ = (100 * int(version_split[0])) + (10 * int(version_split[1])) + (1 * int(version_split[2]))
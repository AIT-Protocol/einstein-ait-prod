import time
import typing
import argparse
import bittensor as bt

# Bittensor Miner Template:
import einstein
from einstein.protocol import CoreSynapse

# import base miner class which takes care of most of the boilerplate
from neurons.miner import Miner


class PhraseMiner(Miner):
    """
    This little fella responds with whatever phrase you give it.
    """

    @classmethod
    def add_args(cls, parser: argparse.ArgumentParser):

        super().add_args(parser)

        parser.add_argument(
            "--neuron.phrase",
            type=str,
            help="The phrase to use when running a phrase (test) miner.",
            default="Can you please repeat that?",
        )

    def __init__(self, config=None):
        super().__init__(config=config)

    async def forward(self, synapse: CoreSynapse) -> CoreSynapse:

        synapse.completion = self.config.neuron.phrase
        self.step += 1
        return synapse

    async def blacklist(self, synapse: CoreSynapse) -> typing.Tuple[bool, str]:
        return False, "All good here"

    async def priority(self, synapse: CoreSynapse) -> float:
        return 1e6


# This is the main function, which runs the miner.
if __name__ == "__main__":
    with PhraseMiner() as miner:
        while True:
            miner.log_status()
            time.sleep(5)

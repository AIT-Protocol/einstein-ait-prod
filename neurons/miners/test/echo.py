import time
import typing
import bittensor as bt

# Bittensor Miner Template:
import einstein
from einstein.protocol import CoreSynapse

# import base miner class which takes care of most of the boilerplate
from neurons.miner import Miner


class EchoMiner(Miner):
    """
    This little fella just repeats the last message it received.
    """

    def __init__(self, config=None):
        super().__init__(config=config)

    async def forward(self, synapse: CoreSynapse) -> CoreSynapse:

        synapse.completion = synapse.messages[-1]
        self.step += 1
        return synapse

    async def blacklist(self, synapse: CoreSynapse) -> typing.Tuple[bool, str]:
        return False, "All good here"

    async def priority(self, synapse: CoreSynapse) -> float:
        return 1e6


# This is the main function, which runs the miner.
if __name__ == "__main__":
    with EchoMiner() as miner:
        while True:
            bt.logging.info("Miner running...", time.time())
            time.sleep(5)

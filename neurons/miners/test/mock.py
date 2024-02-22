import time
import typing
import bittensor as bt

# Bittensor Miner Template:
import einstein
from einstein.protocol import CoreSynapse

# import base miner class which takes care of most of the boilerplate
from neurons.miner import Miner


class MockMiner(Miner):
    """
    This little fella responds with a static message.
    """

    def __init__(self, config=None):
        super().__init__(config=config)

    async def forward(self, synapse: CoreSynapse) -> CoreSynapse:

        synapse.completion = f"Hey you reached mock miner {self.config.wallet.hotkey!r}. Please leave a message after the tone.. Beep!"

        return synapse

    async def blacklist(self, synapse: CoreSynapse) -> typing.Tuple[bool, str]:
        return False, "All good here"

    async def priority(self, synapse: CoreSynapse) -> float:
        return 1e6


# This is the main function, which runs the miner.
if __name__ == "__main__":
    with MockMiner() as miner:
        while True:
            bt.logging.info("Miner running...", time.time())
            time.sleep(5)

import time
import typing
import bittensor as bt

# Bittensor Miner Template:
import einstein
from einstein.protocol import StreamCoreSynapse

# import base miner class which takes care of most of the boilerplate
from einstein.base.einstein_miner import Miner


class MockMiner(Miner):
    """
    This little fella responds with a static message.
    """

    def __init__(self, config=None):
        super().__init__(config=config)

    async def forward(self, synapse: StreamCoreSynapse) -> StreamCoreSynapse:

        synapse.completion = f"Hey you reached mock miner {self.config.wallet.hotkey!r}. Please leave a message after the tone.. Beep!"
        self.step += 1
        return synapse

    async def blacklist(self, synapse: StreamCoreSynapse) -> typing.Tuple[bool, str]:
        return False, "All good here"

    async def priority(self, synapse: StreamCoreSynapse) -> float:
        return 1e6


# This is the main function, which runs the miner.
if __name__ == "__main__":
    with MockMiner() as miner:
        while True:
            miner.log_status()
            time.sleep(5)

import time
import typing
import bittensor as bt

# Bittensor Miner Template:
import einstein
from einstein.protocol import StreamCoreSynapse

# import base miner class which takes care of most of the boilerplate
from einstein.base.einstein_miner import Miner


class EchoMiner(Miner):
    """
    This little fella just repeats the last message it received.
    """

    def __init__(self, config=None):
        super().__init__(config=config)

    async def forward(self, synapse: StreamCoreSynapse) -> StreamCoreSynapse:

        synapse.completion = synapse.messages[-1]
        self.step += 1
        return synapse

    async def blacklist(self, synapse: StreamCoreSynapse) -> typing.Tuple[bool, str]:
        return False, "All good here"

    async def priority(self, synapse: StreamCoreSynapse) -> float:
        return 1e6


# This is the main function, which runs the miner.
if __name__ == "__main__":
    with EchoMiner() as miner:
        while True:
            miner.log_status()
            time.sleep(5)

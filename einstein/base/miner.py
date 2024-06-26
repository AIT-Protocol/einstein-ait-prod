import time
import torch
import argparse
import asyncio
import threading
import bittensor as bt
from einstein.base.neuron import BaseNeuron
from einstein.utils.config import add_miner_args
from einstein.protocol import StreamCoreSynapse
from traceback import print_exception


class BaseStreamMinerNeuron(BaseNeuron):
    """
    Base class for Bittensor miners.
    """

    @classmethod
    def add_args(cls, parser: argparse.ArgumentParser):
        super().add_args(parser)
        add_miner_args(cls, parser)

    def __init__(self, config=None):
        super().__init__(config=config)

        # Warn if allowing incoming requests from anyone.
        if not self.config.blacklist.force_validator_permit:
            bt.logging.warning(
                "You are allowing non-validators to send requests to your miner. This is a security risk."
            )
        if self.config.blacklist.allow_non_registered:
            bt.logging.warning(
                "You are allowing non-registered entities to send requests to your miner. This is a security risk."
            )

        # The axon handles request processing, allowing validators to send this miner requests.
        self.axon = bt.axon(wallet=self.wallet, config=self.config)

        # Attach determiners which functions are called when servicing a request.
        bt.logging.info(f"Attaching forward function to miner axon.")
        self.axon.attach(
            forward_fn=self._forward,
            blacklist_fn=self.blacklist,
            priority_fn=self.priority,
        )
        bt.logging.info(f"Axon created: {self.axon}")

        # Instantiate runners
        self.should_exit: bool = False
        self.is_running: bool = False
        self.thread: threading.Thread = None
        self.lock = asyncio.Lock()

    def run(self):
        """
        Initiates and manages the main loop for the miner on the Bittensor network. The main loop handles graceful shutdown on keyboard interrupts and logs unforeseen errors.

        This function performs the following primary tasks:
        1. Check for registration on the Bittensor network.
        2. Starts the miner's axon, making it active on the network.
        3. Periodically resynchronizes with the chain; updating the metagraph with the latest network state and setting weights.

        The miner continues its operations until `should_exit` is set to True or an external interruption occurs.
        During each epoch of its operation, the miner waits for new blocks on the Bittensor network, updates its
        knowledge of the network (metagraph), and sets its weights. This process ensures the miner remains active
        and up-to-date with the network's latest state.

        Note:
            - The function leverages the global configurations set during the initialization of the miner.
            - The miner's axon serves as its interface to the Bittensor network, handling incoming and outgoing requests.

        Raises:
            KeyboardInterrupt: If the miner is stopped by a manual interruption.
            Exception: For unforeseen errors during the miner's operation, which are logged for diagnosis.
        """
        
        # # Create event loop
        # loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(loop)

        # Check that miner is registered on the network.
        self.sync()

        # Serve passes the axon information to the network + netuid we are hosting on.
        # This will auto-update if the axon port of external ip have changed.
        bt.logging.info(
            f"Serving miner axon {self.axon} on network: {self.config.subtensor.chain_endpoint} with netuid: {self.config.netuid}"
        )
        self.axon.serve(netuid=self.config.netuid, subtensor=self.subtensor)

        # Start  starts the miner's axon, making it active on the network.
        self.axon.start()

        bt.logging.info(f"Miner starting at block: {self.block}")
        last_update_block = 0

        # This loop maintains the miner's operations until intentionally stopped.
        try:
            while not self.should_exit:
                while (
                    self.block - last_update_block
                    < self.config.neuron.epoch_length
                ):
                    # Wait before checking again.
                    time.sleep(1)

                    # Check if we should exit.
                    if self.should_exit:
                        break

                # Sync metagraph and potentially set weights.
                self.sync()
                last_update_block = self.block
                self.step += 1

        # If someone intentionally stops the miner, it'll safely terminate operations.
        except KeyboardInterrupt:
            self.axon.stop()
            bt.logging.success("Miner killed by keyboard interrupt.")
            exit()

        # In case of unforeseen errors, the miner will log the error and continue operations.
        except Exception as err:
            bt.logging.error("Error during mining", str(err))
            bt.logging.debug(print_exception(type(err), err, err.__traceback__))
            self.should_exit = True

    def run_in_background_thread(self):
        """
        Starts the miner's operations in a separate background thread.
        This is useful for non-blocking operations.
        """
        if not self.is_running:
            bt.logging.debug("Starting miner in background thread.")
            self.should_exit = False
            self.thread = threading.Thread(target=self.run, daemon=True)
            self.thread.start()
            self.is_running = True
            bt.logging.debug("Started")

    def stop_run_thread(self):
        """
        Stops the miner's operations that are running in the background thread.
        """
        if self.is_running:
            bt.logging.debug("Stopping miner in background thread.")
            self.should_exit = True
            self.thread.join(5)
            self.is_running = False
            bt.logging.debug("Stopped")

    def __enter__(self):
        """
        Starts the miner's operations in a background thread upon entering the context.
        This method facilitates the use of the miner in a 'with' statement.
        """
        self.run_in_background_thread()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Stops the miner's background operations upon exiting the context.
        This method facilitates the use of the miner in a 'with' statement.

        Args:
            exc_type: The type of the exception that caused the context to be exited.
                      None if the context was exited without an exception.
            exc_value: The instance of the exception that caused the context to be exited.
                       None if the context was exited without an exception.
            traceback: A traceback object encoding the stack trace.
                       None if the context was exited without an exception.
        """
        self.stop_run_thread()
    
    def set_weights(self):
        """
        Self-assigns a weight of 1 to the current miner (identified by its UID) and
        a weight of 0 to all other peers in the network. The weights determine the trust level the miner assigns to other nodes on the network.
        Raises:
            Exception: If there's an error while setting weights, the exception is logged for diagnosis.
        """
        # try:
        #     # --- query the chain for the most current number of peers on the network
        #     chain_weights = torch.zeros(
        #         self.subtensor.subnetwork_n(netuid=self.metagraph.netuid)
        #     )
        #     chain_weights[self.uid] = 1

        #     # --- Set weights.
        #     self.subtensor.set_weights(
        #         wallet=self.wallet,
        #         netuid=self.metagraph.netuid,
        #         uids=torch.arange(0, len(chain_weights)),
        #         weights=chain_weights.to("cpu"),
        #         wait_for_inclusion=False,
        #         version_key=self.spec_version,
        #     )

        # except Exception as e:
        #     bt.logging.error(
        #         f"Failed to set weights on chain with exception: { e }"
        #     )

        # bt.logging.info(f"Set weights: {chain_weights}")
        pass

    def resync_metagraph(self):
        """Resyncs the metagraph and updates the hotkeys and moving averages based on the new metagraph."""
        bt.logging.info("\033[1;33mResyncing the metagraph...\033[0m")

        # Sync the metagraph.
        self.metagraph.sync(subtensor=self.subtensor)

    def _forward(self, synapse: StreamCoreSynapse) -> StreamCoreSynapse:
        """
        A wrapper method around the `forward` method that will be defined by the subclass.
        This method acts as an intermediary layer to perform pre-processing before calling the
        actual `forward` method implemented in the subclass. Specifically, it checks whether a
        prompt is in cache to avoid reprocessing recent requests. If the prompt is not in the
        cache, the subclass `forward` method is called.
        Args:
            synapse (StreamCoreSynapse): The incoming request object encapsulating the details of the request.
        Returns:
            StreamCoreSynapse: The response object to be sent back in reply to the incoming request, essentially
            the filled synapse request object.
        Raises:
            ValueError: If the prompt is found in the cache indicating it was sent recently.
        Example:
            This method is not meant to be called directly but is invoked internally when a request
            is received, and it subsequently calls the `forward` method of the subclass.
        """
        return self.forward(synapse=synapse)

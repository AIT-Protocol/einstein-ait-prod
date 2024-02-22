import torch
import random
import bittensor as bt
from typing import List


def check_uid_availability(
    metagraph: "bt.metagraph.Metagraph", uid: int, vpermit_tao_limit: int, coldkeys: set = None, ips: set = None,
) -> bool:
    """Check if uid is available. The UID should be available if it is serving and has less than vpermit_tao_limit stake
    Args:
        metagraph (:obj: bt.metagraph.Metagraph): Metagraph object
        uid (int): uid to be checked
        vpermit_tao_limit (int): Validator permit tao limit
        coldkeys (set): Set of coldkeys to exclude
        ips (set): Set of ips to exclude
    Returns:
        bool: True if uid is available, False otherwise
    """
    # Filter non serving axons.
    if not metagraph.axons[uid].is_serving:
        bt.logging.debug(f"uid: {uid} is not serving")
        return False
      
    # Filter validator permit > 1024 stake.
    if metagraph.validator_permit[uid] and metagraph.S[uid] > vpermit_tao_limit:
        bt.logging.debug(f"uid: {uid} has vpermit and stake ({metagraph.S[uid]}) > {vpermit_tao_limit}")
        return False

    if coldkeys and metagraph.axons[uid].coldkey in coldkeys:
        return False

    if ips and metagraph.axons[uid].ip in ips:
        return False

    # Available otherwise.
    return True


def get_random_uids(
    self, k: int, exclude: List[int] = None
) -> torch.LongTensor:
    """Returns k available random uids from the metagraph.
    Args:
        k (int): Number of uids to return.
        exclude (List[int]): List of uids to exclude from the random sampling.
    Returns:
        uids (torch.LongTensor): Randomly sampled available uids.
    Notes:
        If `k` is larger than the number of available `uids`, set `k` to the number of available `uids`.
    """
    candidate_uids = []
    avail_uids = []
    coldkeys = set()
    ips = set()
    for uid in range(self.metagraph.n.item()):
        if uid == self.uid:
            continue

        uid_is_available = check_uid_availability(
            self.metagraph, uid, self.config.neuron.vpermit_tao_limit, coldkeys, ips,
        )
        if not uid_is_available:
            continue

        if self.config.neuron.query_unique_coldkeys:
            coldkeys.add(self.metagraph.axons[uid].coldkey)

        if self.config.neuron.query_unique_ips:
            ips.add(self.metagraph.axons[uid].ip)

        avail_uids.append(uid)
        if exclude is None or uid not in exclude:
            candidate_uids.append(uid)

    # Adjust k if it exceeds the number of available candidate UIDs
    k = min(k, len(candidate_uids))

    # If there are not enough candidates to meet k, use all available uids
    if len(candidate_uids) < k:
        if len(avail_uids) >= k:  # Ensure there's enough in avail_uids to supplement
            difference = k - len(candidate_uids)
            additional_uids = random.sample([uid for uid in avail_uids if uid not in candidate_uids], difference)
            available_uids = candidate_uids + additional_uids
        else:  # If not, just use what's available
            available_uids = candidate_uids
    else:
        available_uids = candidate_uids

    # Now, k should never exceed the length of available_uids
    if len(available_uids) < k:  # Additional check to prevent sampling more than available
        k = len(available_uids)
    uids = torch.tensor(random.sample(available_uids, k)) if k > 0 else torch.tensor([])
    return uids

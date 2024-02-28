import time
from abc import ABC, abstractmethod
from typing import Dict
import bittensor as bt

from ..selector import Selector
from .context import Context


class Dataset(ABC):
    """Base class for datasets."""

    max_tries: int = 10

    @abstractmethod
    def search(self, name):
        ...

    @abstractmethod
    def random(self, name):
        ...

    @abstractmethod
    def get(self, name):
        ...

    def next(self, method: str = 'random', selector: Selector = Selector(), **kwargs) -> Dict:
        tries = 1
        t0 = time.time()

        while True:

            # TODO: Multithread the get method so that we don't have to suffer nonexistent pages
            info = {}
            if method == 'random':
                info = self.random(selector=selector, **kwargs)
            elif method == 'search':
                info = self.search(selector=selector, **kwargs)
            elif method == 'get':
                info = self.get(selector=selector, **kwargs)
            else:
                raise ValueError(f"Unknown dataset get method {method!r}")

            if info:
                break

            bt.logging.warning(f"Could not find an sample which meets {self.__class__.__name__} requirements after {tries} tries. Retrying... ({self.max_tries - tries} tries remaining.)")

            tries += 1
            if tries == self.max_tries:
                raise Exception(
                    f"Could not find an sample which meets {self.__class__.__name__} requirements after {tries} tries."
                )

        info['stats'] = {
            'creator': self.__class__.__name__,
            'fetch_time': time.time() - t0,
            'num_tries': tries,
            'fetch_method': method,
            'next_kwargs': kwargs
            }
        return Context(**info)
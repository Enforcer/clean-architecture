from abc import (
    ABCMeta,
    abstractmethod
)


class AuctionsRepository(metaclass=ABCMeta):
    @abstractmethod
    def get(self, auction_id):
        pass

    @abstractmethod
    def save(self, auction):
        pass

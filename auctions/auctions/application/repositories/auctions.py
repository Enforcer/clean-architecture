from abc import (
    ABCMeta,
    abstractmethod
)

from auctions.domain.entities import Auction


class AuctionsRepository(metaclass=ABCMeta):
    @abstractmethod
    def get(self, auction_id) -> Auction:
        pass

    @abstractmethod
    def save(self, auction: Auction) -> None:
        pass

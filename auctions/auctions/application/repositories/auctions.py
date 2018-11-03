from abc import (
    ABCMeta,
    abstractmethod
)

from auctions.domain.entities import Auction
from auctions.domain.types import AuctionId


class AuctionsRepository(metaclass=ABCMeta):

    @abstractmethod
    def get(self, auction_id: AuctionId) -> Auction:
        pass

    @abstractmethod
    def save(self, auction: Auction) -> None:
        pass

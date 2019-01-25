import abc
from typing import List

from auctions.domain.entities import Auction
from auctions.domain.types import AuctionId


class AuctionsRepository(abc.ABC):

    @abc.abstractmethod
    def get(self, auction_id: AuctionId) -> Auction:
        pass

    @abc.abstractmethod
    def save(self, auction: Auction) -> None:
        pass

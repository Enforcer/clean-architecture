import abc
from dataclasses import dataclass
from datetime import datetime
from typing import List

from foundation.value_objects import Money


@dataclass
class AuctionDto:
    id: int
    title: str
    current_price: Money
    starting_price: Money
    ends_at: datetime


class GetSingleAuction(abc.ABC):
    @abc.abstractmethod
    def query(self, auction_id: int) -> AuctionDto:
        pass


class GetActiveAuctions(abc.ABC):
    @abc.abstractmethod
    def query(self) -> List[AuctionDto]:
        pass

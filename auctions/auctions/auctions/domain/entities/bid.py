from dataclasses import dataclass
from typing import Optional

from auctions.domain.types import BidderId, BidId
from auctions.domain.value_objects import Money


@dataclass(unsafe_hash=True)
class Bid:
    id: Optional[BidId]
    bidder_id: BidderId
    amount: Money

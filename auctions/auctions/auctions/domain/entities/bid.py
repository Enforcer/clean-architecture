from dataclasses import dataclass
from typing import Optional

from foundation.value_objects import Money

from auctions.domain.types import BidderId, BidId


@dataclass(unsafe_hash=True)
class Bid:
    id: Optional[BidId]
    bidder_id: BidderId
    amount: Money

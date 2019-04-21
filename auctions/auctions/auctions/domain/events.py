from dataclasses import dataclass

from auctions.domain.value_objects import Money
from auctions.domain.types import AuctionId, BidderId

from foundation.events import Event


@dataclass(frozen=True)
class BidderHasBeenOverbid(Event):
    auction_id: AuctionId
    bidder_id: BidderId
    new_price: Money


@dataclass(frozen=True)
class WinningBidPlaced(Event):
    auction_id: AuctionId
    bidder_id: BidderId
    bid_amount: Money

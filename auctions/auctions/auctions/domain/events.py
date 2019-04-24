from dataclasses import dataclass

from foundation.events import Event
from foundation.value_objects import Money

from auctions.domain.types import AuctionId, BidderId


@dataclass(frozen=True)
class BidderHasBeenOverbid(Event):
    auction_id: AuctionId
    bidder_id: BidderId
    new_price: Money
    auction_title: str


@dataclass(frozen=True)
class WinningBidPlaced(Event):
    auction_id: AuctionId
    bidder_id: BidderId
    bid_amount: Money
    auction_title: str

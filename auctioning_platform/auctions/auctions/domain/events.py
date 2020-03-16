from dataclasses import dataclass
from typing import Optional

from foundation.events import Event
from foundation.value_objects import Money

from auctions.domain.value_objects import AuctionId, BidderId


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


@dataclass(frozen=True)
class AuctionEnded(Event):
    auction_id: AuctionId
    winner_id: Optional[BidderId]
    winning_bid: Money
    auction_title: str


@dataclass(frozen=True)
class AuctionBegan(Event):
    auction_id: AuctionId
    starting_price: Money
    auction_title: str

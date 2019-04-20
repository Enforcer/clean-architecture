from dataclasses import dataclass

from auctions.domain.value_objects import Money
from auctions.domain.types import AuctionId, BidderId


@dataclass
class BidderHasBeenOverbid:
    auction_id: AuctionId
    bidder_id: BidderId
    new_price: Money


@dataclass
class WinningBidPlaced:
    auction_id: AuctionId
    bidder_id: BidderId
    bid_amount: Money

from typing import List
from datetime import datetime

from auctions.domain.entities.bid import Bid
from auctions.domain.types import (
    AuctionId,
    BidId,
    BidderId,
)
from auctions.domain.value_objects import Money
from auctions.domain.exceptions import BidOnEndedAuctionError


class Auction:
    def __init__(
            self,
            id: AuctionId,
            title: str,
            starting_price: Money,
            bids: List[Bid],
            ends_at: datetime,
    ) -> None:
        assert isinstance(starting_price, Money)
        self.id = id
        self.title = title
        self.starting_price = starting_price
        self.bids = sorted(bids, key=lambda bid: bid.amount)
        self.ends_at = ends_at
        self._withdrawn_bids_ids: List[BidId] = []

    def place_bid(self, bidder_id: BidderId, amount: Money) -> None:
        if datetime.now() > self.ends_at:
            raise BidOnEndedAuctionError

        if amount > self.current_price:
            self.bids.append(Bid(id=None, bidder_id=bidder_id, amount=amount))

    @property
    def current_price(self) -> Money:
        if not self.bids:
            return self.starting_price
        else:
            return self._highest_bid.amount

    @property
    def winners(self) -> List[BidderId]:
        if not self.bids:
            return []
        return [self._highest_bid.bidder_id]

    @property
    def _highest_bid(self) -> Bid:
        return self.bids[-1]

    def withdraw_bids(self, bids_ids: List[int]):
        self.bids = [bid for bid in self.bids if bid.id not in bids_ids]
        self._withdrawn_bids_ids.extend(bids_ids)

    @property
    def withdrawn_bids_ids(self) -> List[BidId]:
        return self._withdrawn_bids_ids[:]

    def __str__(self):
        return f'<Auction #{self.id} title="{self.title}" current_price={self.current_price}>'

    def __eq__(self, other: 'Auction') -> bool:
        return isinstance(other, Auction) and vars(self) == vars(other)

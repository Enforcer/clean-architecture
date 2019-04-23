from typing import List
from datetime import datetime

from foundation.events import Event

from auctions.domain.entities.bid import Bid
from auctions.domain.events import BidderHasBeenOverbid, WinningBidPlaced
from auctions.domain.types import AuctionId, BidId, BidderId
from auctions.domain.value_objects import Money
from auctions.domain.exceptions import BidOnEndedAuction


class Auction:
    def __init__(self, id: AuctionId, title: str, starting_price: Money, bids: List[Bid], ends_at: datetime) -> None:
        assert isinstance(starting_price, Money)
        self.id = id
        self.title = title
        self.starting_price = starting_price
        self.bids = sorted(bids, key=lambda bid: bid.amount)
        self.ends_at = ends_at
        self._withdrawn_bids_ids: List[BidId] = []
        self._pending_domain_events: List[Event] = []

    def _record_event(self, event: object) -> None:
        self._pending_domain_events.append(event)

    @property
    def domain_events(self) -> list:
        return self._pending_domain_events[:]

    def place_bid(self, bidder_id: BidderId, amount: Money) -> None:
        if datetime.now(tz=self.ends_at.tzinfo) > self.ends_at:
            raise BidOnEndedAuction

        old_winner = self.winners[0] if self.bids else None
        if amount > self.current_price:
            self.bids.append(Bid(id=None, bidder_id=bidder_id, amount=amount))
            self._record_event(WinningBidPlaced(self.id, bidder_id, amount, self.title))
            if old_winner:
                self._record_event(BidderHasBeenOverbid(self.id, old_winner, amount, self.title))

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

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Auction) and vars(self) == vars(other)

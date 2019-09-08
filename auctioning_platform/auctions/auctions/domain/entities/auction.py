from datetime import datetime
from typing import List, Optional

from foundation.events import EventMixin
from foundation.value_objects import Money

from auctions.domain.entities.bid import Bid
from auctions.domain.events import AuctionEnded, BidderHasBeenOverbid, WinningBidPlaced
from auctions.domain.exceptions import AuctionAlreadyEnded, AuctionHasNotEnded, BidOnEndedAuction
from auctions.domain.types import AuctionId, BidderId, BidId


class Auction(EventMixin):
    def __init__(
        self, id: AuctionId, title: str, starting_price: Money, bids: List[Bid], ends_at: datetime, ended: bool
    ) -> None:
        super().__init__()
        self.id = id
        self.title = title
        self.starting_price = starting_price
        self.bids = sorted(bids, key=lambda bid: bid.amount)
        self.ends_at = ends_at
        self.ended = ended
        self._withdrawn_bids_ids: List[BidId] = []

    def place_bid(self, bidder_id: BidderId, amount: Money) -> None:
        if self.should_end:
            raise BidOnEndedAuction

        old_winner = self.winners[0] if self.bids else None
        if amount > self.current_price:
            self.bids.append(Bid(id=None, bidder_id=bidder_id, amount=amount))
            self._record_event(WinningBidPlaced(self.id, bidder_id, amount, self.title))
            if old_winner:
                self._record_event(BidderHasBeenOverbid(self.id, old_winner, amount, self.title))

    @property
    def should_end(self) -> bool:
        return datetime.now(tz=self.ends_at.tzinfo) > self.ends_at

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

    def withdraw_bids(self, bids_ids: List[int]) -> None:
        self.bids = [bid for bid in self.bids if bid.id not in bids_ids]
        self._withdrawn_bids_ids.extend(bids_ids)

    @property
    def withdrawn_bids_ids(self) -> List[BidId]:
        return self._withdrawn_bids_ids[:]

    def end_auction(self) -> None:
        if not self.should_end:
            raise AuctionHasNotEnded
        if self.ended:
            raise AuctionAlreadyEnded

        winner_id: Optional[BidderId] = None
        if self.bids:
            winner_id = self._highest_bid.bidder_id

        self.ended = True
        self._record_event(AuctionEnded(self.id, winner_id, self.current_price, self.title))

    def __str__(self) -> str:
        return f'<Auction #{self.id} title="{self.title}" current_price={self.current_price}>'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Auction) and vars(self) == vars(other)

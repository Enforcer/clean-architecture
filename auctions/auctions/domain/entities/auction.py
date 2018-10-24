import typing

from auctions.domain.entities.bid import Bid
from auctions.domain.value_objects import Money


class Auction:
    def __init__(self, id: int, title: str, initial_price: Money, bids: typing.List[Bid]) -> None:
        assert isinstance(initial_price, Money)
        self.id = id
        self.title = title
        self.initial_price = initial_price
        self.bids = sorted(bids, key=lambda bid: bid.amount)
        self.withdrawn_bids_ids: typing.List[int] = []

    def make_a_bid(self, bid: Bid):
        if bid.amount > self.current_price:
            self.bids.append(bid)

    @property
    def current_price(self) -> Money:
        if not self.bids:
            return self.initial_price
        else:
            return self._highest_bid.amount

    @property
    def winners(self):
        if not self.bids:
            return []
        return [self._highest_bid.bidder_id]

    @property
    def _highest_bid(self) -> Bid:
        return self.bids[-1]

    def withdraw_bids(self, bids_ids: typing.List[int]):
        self.bids = [bid for bid in self.bids if bid.id not in bids_ids]
        self.withdrawn_bids_ids.extend(bids_ids)

    def __str__(self):
        return f'<Auction #{self.id} title="{self.title}" current_price={self.current_price}>'

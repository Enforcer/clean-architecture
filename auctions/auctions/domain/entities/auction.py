import typing
from decimal import Decimal

from auctions.domain.entities.bid import Bid


class Auction:
    def __init__(self, id: int, title: str, initial_price: Decimal, bids: typing.List[Bid]):
        self.id = id
        self.title = title
        self.initial_price = initial_price
        self.bids = sorted(bids, key=lambda bid: bid.amount)
        self.withdrawn_bids_ids = []

    def make_a_bid(self, bid: Bid):
        if bid.amount > self.current_price:
            self.bids.append(bid)

    @property
    def current_price(self) -> Decimal:
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

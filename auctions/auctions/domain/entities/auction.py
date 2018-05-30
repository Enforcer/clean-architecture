import typing
from decimal import Decimal

from auctions.domain.entities.bid import Bid


class Auction:
    def __init__(self, id: int, initial_price: Decimal, bids: typing.List[Bid]):
        self.id = id
        self.initial_price = initial_price
        self.bids = bids

    def withdraw_bids(self, bids_ids: typing.List[int]):
        raise NotImplementedError

    def make_a_bid(self, bid: Bid):
        # TODO
        pass

    @property
    def winners(self):
        # Currently support for only one winner
        if not self.bids:
            return []
        highest_bid = sorted(self.bids, key=lambda bid: bid.amount, reverse=True)[0]
        return [highest_bid.user_id]

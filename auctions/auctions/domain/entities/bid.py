from typing import Optional

from auctions.domain.value_objects import Money


class Bid:
    def __init__(self, id: Optional[int], bidder_id: int, amount: Money) -> None:
        assert isinstance(amount, Money)
        self.id = id
        self.bidder_id = bidder_id
        self.amount = amount

    def __eq__(self, other) -> bool:
        return type(self) == type(other) and vars(self) == vars(other)

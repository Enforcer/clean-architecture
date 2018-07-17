from typing import Optional
from decimal import Decimal


class Bid:
    def __init__(self, id: Optional[int], bidder_id: int, amount: Decimal) -> None:
        self.id = id
        self.bidder_id = bidder_id
        self.amount = amount

    def __eq__(self, other) -> bool:
        return type(self) == type(other) and vars(self) == vars(other)

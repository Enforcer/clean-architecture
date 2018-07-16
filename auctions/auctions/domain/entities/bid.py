from typing import Optional
from decimal import Decimal


class Bid:
    def __init__(self, id: Optional[int], user_id: int, amount: Decimal) -> None:
        self.id = id
        self.user_id = user_id
        self.amount = amount

    def __eq__(self, other) -> bool:
        return type(self) == type(other) and vars(self) == vars(other)

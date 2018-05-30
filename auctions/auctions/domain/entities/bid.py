from decimal import Decimal


class Bid:
    def __init__(self, user_id: int, amount: Decimal):
        self.user_id = user_id
        self.amount = amount

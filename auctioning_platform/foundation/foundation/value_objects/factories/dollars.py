from decimal import Decimal
from typing import Union

from foundation.value_objects import Money, currency


def get_dollars(amount: Union[Decimal, str, float, int]) -> Money:
    return Money(currency.USD, amount)

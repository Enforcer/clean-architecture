from decimal import Decimal, DecimalException
from functools import total_ordering
import inspect
from typing import Any, Type

from foundation.value_objects.currency import Currency


@total_ordering
class Money:
    def __init__(self, currency: Type[Currency], amount: Any) -> None:
        if not inspect.isclass(currency) or not issubclass(currency, Currency):
            raise ValueError(f"{currency} is not a subclass of Currency!")
        try:
            decimal_amount = Decimal(amount).normalize()
        except DecimalException:
            raise ValueError(f'"{amount}" is not a valid amount!')
        else:
            decimal_tuple = decimal_amount.as_tuple()
            if decimal_tuple.sign:
                raise ValueError("amount must not be negative!")
            elif -decimal_tuple.exponent > currency.decimal_precision:
                raise ValueError(
                    f"given amount has invalid precision! It should have "
                    f"no more than {currency.decimal_precision} decimal places!"
                )

            self._currency = currency
            self._amount = decimal_amount

    @property
    def currency(self) -> Type[Currency]:
        return self._currency

    @property
    def amount(self) -> Decimal:
        return self._amount

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            raise TypeError
        return self.currency == other.currency and self.amount == other.amount

    def __lt__(self, other: "Money") -> bool:
        if not isinstance(other, Money):
            raise TypeError(f"'<' not supported between instances of 'Money' and '{other.__class__.__name__}'")
        elif self.currency != other.currency:
            raise TypeError("Can not compare money in different currencies!")
        else:
            return self.amount < other.amount

    def __add__(self, other: "Money") -> "Money":
        if not isinstance(other, Money) or not self.currency == other.currency:
            raise TypeError
        return Money(self.currency, self.amount + other.amount)

    def __sub__(self, other: "Money") -> "Money":
        if not isinstance(other, Money) or not self.currency == other.currency:
            raise TypeError
        return Money(self.currency, self.amount - other.amount)

    def __repr__(self) -> str:
        return f"Money({self._currency.__name__}, {repr(self._amount)})"

    def __str__(self) -> str:
        return f"{self._amount} {self._currency.symbol}"

    def __hash__(self) -> int:
        return hash((self.amount, self.currency))

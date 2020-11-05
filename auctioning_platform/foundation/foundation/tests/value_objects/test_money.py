from decimal import Decimal
import operator
from typing import Any, Callable

import pytest

from foundation.value_objects import Currency, Money
from foundation.value_objects.currency import USD


class BTC(Currency):
    decimal_precision = 8
    symbol = "Ƀ"


@pytest.mark.parametrize("currency, amount", [(None, None), (USD, "bazinga"), ("bazinga", "10"), (USD, "15.10001")])
def test_invalid_inputs(currency: object, amount: object) -> None:
    """
    Test if the given inputs are valid.

    Args:
        currency: (todo): write your description
        amount: (int): write your description
    """
    with pytest.raises(ValueError):
        Money(currency, amount)  # type: ignore


@pytest.mark.parametrize("currency, amount", [(USD, "9.99"), (BTC, "1.00000020")])
def test_valid_inputs(currency: object, amount: object) -> None:
    """
    Test that all valid inputs.

    Args:
        currency: (todo): write your description
        amount: (int): write your description
    """
    assert Money(currency, amount)  # type: ignore


@pytest.mark.parametrize(
    "money_instance, expected_repr",
    [
        (Money(USD, "18.59"), "Money(USD, Decimal('18.59'))"),
        (Money(BTC, "12.12345678"), "Money(BTC, Decimal('12.12345678'))"),
    ],
)
def test_repr(money_instance: Money, expected_repr: str) -> None:
    """
    Assert : attr : base.

    Args:
        money_instance: (str): write your description
        expected_repr: (str): write your description
    """
    assert repr(money_instance) == expected_repr


@pytest.mark.parametrize(
    "money_instance, expected_str", [(Money(USD, "12.49"), "12.49 $"), (Money(BTC, "0.00004212"), "0.00004212 Ƀ")]
)
def test_str(money_instance: Money, expected_str: str) -> None:
    """
    Takes a string and adds a string and adds the expected string.

    Args:
        money_instance: (todo): write your description
        expected_str: (str): write your description
    """
    assert str(money_instance) == expected_str


@pytest.mark.parametrize(
    "one, another, expected",
    [
        (Money(USD, "12.49"), Money(USD, "12.49"), True),
        (Money(USD, "8.99"), Money(BTC, "8.99"), False),
        (Money(USD, "8"), Money(USD, "0.12"), False),
        (Money(BTC, "0.1"), Money(USD, "149.99"), False),
    ],
)
def test_equality(one: Money, another: Money, expected: bool) -> None:
    """
    Assert that the given one exists.

    Args:
        one: (str): write your description
        another: (todo): write your description
        expected: (todo): write your description
    """
    assert (one == another) == expected


def test_lt_the_same_currency() -> None:
    """
    Determine whether the currency

    Args:
    """
    assert Money(USD, "12.49") < Money(USD, "15.00")


def test_lt_different_currency() -> None:
    """
    Test if the currency is a currency.

    Args:
    """
    with pytest.raises(TypeError):
        assert Money(BTC, "0.49000012") < Money(USD, "12.49")


@pytest.mark.parametrize(
    "one, another, cmp_operator, expected_result",
    [
        (Money(USD, "1"), Money(USD, "2"), operator.gt, False),
        (Money(USD, "1"), Money(USD, "0.49"), operator.gt, True),
        (Money(USD, "2"), Money(USD, "3"), operator.ge, False),
        (Money(USD, "5"), Money(USD, "5.00"), operator.ge, True),
    ],
)
def test_supports_different_comparison_operators(
    one: Money, another: Money, cmp_operator: Callable[[Money, Money], bool], expected_result: bool
) -> None:
    """
    Tests if the given operators are true.

    Args:
        one: (todo): write your description
        another: (todo): write your description
        cmp_operator: (todo): write your description
        Callable: (todo): write your description
        expected_result: (todo): write your description
    """
    assert cmp_operator(one, another) == expected_result


@pytest.mark.parametrize(
    "one, another, math_operator, expected_result",
    [
        (Money(USD, "1"), Money(USD, "2"), operator.add, Money(USD, "3")),
        (Money(USD, "1"), Money(USD, "0.49"), operator.sub, Money(USD, "0.51")),
    ],
)
def test_supports_basic_math_operators_if_the_same_currency(
    one: Money, another: Money, math_operator: Callable[[Money, Money], Money], expected_result: Money
) -> None:
    """
    Test if the result of - test_operator_the_operator.

    Args:
        one: (todo): write your description
        another: (todo): write your description
        math_operator: (todo): write your description
        Callable: (str): write your description
        expected_result: (todo): write your description
    """
    assert math_operator(one, another) == expected_result


@pytest.mark.parametrize(
    "arg, expected_result", [("5.0000", Money(USD, "5")), (Decimal("5.990000000"), Money(USD, "5.99"))]
)
def test_normalizes_whenever_it_can(arg: Any, expected_result: Money) -> None:
    """
    Asserts if the given callable.

    Args:
        arg: (todo): write your description
        expected_result: (str): write your description
    """
    assert Money(USD, arg) == expected_result

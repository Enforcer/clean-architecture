from abc import abstractmethod
from dataclasses import dataclass

from foundation.value_objects import Money


class Email:
    @property
    @abstractmethod
    def title(self) -> str:
        pass

    @property
    @abstractmethod
    def html(self) -> str:
        pass

    @property
    @abstractmethod
    def text(self) -> str:
        pass


@dataclass
class Overbid(Email):
    auction_title: str
    new_price: Money

    @property
    def title(self) -> str:
        return "You have been overbid :("

    @property
    def text(self) -> str:
        return f'A new bid has been placed on the auction "{self.auction_title}". New price is {self.new_price}.'

    @property
    def html(self) -> str:
        return self.text


@dataclass
class Winning(Email):
    auction_title: str
    amount: Money

    @property
    def title(self) -> str:
        return "You are winning :)"

    @property
    def text(self) -> str:
        return f'Congratulations! Your bid {self.amount} is the winning one one the auction "{self.auction_title}"'

    @property
    def html(self) -> str:
        return self.text


@dataclass
class PaymentSuccessful(Email):
    auction_title: str
    paid_price: Money

    @property
    def title(self) -> str:
        return f"Payment for '{self.auction_title}' succeeded"

    @property
    def text(self) -> str:
        return f"Payment {self.paid_price} confirmed, your item is on its way!"

    @property
    def html(self) -> str:
        return self.text

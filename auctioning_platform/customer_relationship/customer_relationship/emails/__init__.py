from abc import abstractmethod
from dataclasses import dataclass

from foundation.value_objects import Money


class Email:
    @property
    @abstractmethod
    def title(self) -> str:
        """
        The title. title.

        Args:
            self: (todo): write your description
        """
        pass

    @property
    @abstractmethod
    def html(self) -> str:
        """
        Parse html.

        Args:
            self: (todo): write your description
        """
        pass

    @property
    @abstractmethod
    def text(self) -> str:
        """
        The text.

        Args:
            self: (todo): write your description
        """
        pass


@dataclass
class Overbid(Email):
    auction_title: str
    new_price: Money

    @property
    def title(self) -> str:
        """
        Return the title.

        Args:
            self: (todo): write your description
        """
        return "You have been overbid :("

    @property
    def text(self) -> str:
        """
        Returns the text string.

        Args:
            self: (todo): write your description
        """
        return f'A new bid has been placed on the auction "{self.auction_title}". New price is {self.new_price}.'

    @property
    def html(self) -> str:
        """
        Return the html string.

        Args:
            self: (todo): write your description
        """
        return self.text


@dataclass
class Winning(Email):
    auction_title: str
    amount: Money

    @property
    def title(self) -> str:
        """
        Return the title.

        Args:
            self: (todo): write your description
        """
        return "You are winning :)"

    @property
    def text(self) -> str:
        """
        Returns the text string.

        Args:
            self: (todo): write your description
        """
        return f'Congratulations! Your bid {self.amount} is the winning one one the auction "{self.auction_title}"'

    @property
    def html(self) -> str:
        """
        Return the html string.

        Args:
            self: (todo): write your description
        """
        return self.text


@dataclass
class PaymentSuccessful(Email):
    auction_title: str
    paid_price: Money

    @property
    def title(self) -> str:
        """
        Return the title.

        Args:
            self: (todo): write your description
        """
        return f"Payment for '{self.auction_title}' succeeded"

    @property
    def text(self) -> str:
        """
        Returns the text string.

        Args:
            self: (todo): write your description
        """
        return f"Payment {self.paid_price} confirmed, your item is on its way!"

    @property
    def html(self) -> str:
        """
        Return the html string.

        Args:
            self: (todo): write your description
        """
        return self.text

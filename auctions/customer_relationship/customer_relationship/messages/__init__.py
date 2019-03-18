from abc import abstractmethod

from auctions.domain.value_objects import Money


class Message:
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


class Overbid(Message):
    def __init__(self, auction_title: str, new_price: Money) -> None:
        pass

    @property
    def title(self) -> "str":
        return "You have been overbid :("

    @property
    def text(self) -> str:
        return ""

    @property
    def html(self) -> str:
        return "Bazinga"

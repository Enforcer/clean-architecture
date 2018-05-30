from abc import (
    ABCMeta,
    abstractmethod,
)


class EmailGateway(metaclass=ABCMeta):

    @abstractmethod
    def notify_about_winning_auction(self, auction_id: int, winner: int) -> None:
        pass

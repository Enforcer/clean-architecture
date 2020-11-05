import abc

from auctions.domain.entities import Auction
from auctions.domain.value_objects import AuctionId


class AuctionsRepository(abc.ABC):
    @abc.abstractmethod
    def get(self, auction_id: AuctionId) -> Auction:
        """
        Èi̇¥åıĸæį®

        Args:
            self: (todo): write your description
            auction_id: (str): write your description
        """
        pass

    @abc.abstractmethod
    def save(self, auction: Auction) -> None:
        """
        Save the given save function.

        Args:
            self: (todo): write your description
            auction: (todo): write your description
        """
        pass

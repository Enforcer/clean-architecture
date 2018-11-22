from abc import (
    ABCMeta,
    abstractmethod,
)
from auctions.domain.types import (
    AuctionId,
    BidderId,
)
from auctions.domain.value_objects import Money


class PaymentFailedError(Exception):
    pass


class PaymentProvider(metaclass=ABCMeta):

    @abstractmethod
    def pay_for_won_auction(self, auction_id: AuctionId, bidder_id: BidderId, charge: Money) -> None:
        pass

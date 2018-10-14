import abc
from decimal import Decimal
from typing import NamedTuple

import inject

from auctions.domain.entities import Bid
from auctions.application.repositories import AuctionsRepository
from auctions.application.interfaces import EmailGateway


class PlacingBidInputDto(NamedTuple):
    bidder_id: int
    auction_id: int
    amount: Decimal


class PlacingBidOutputDto(NamedTuple):
    is_winner: bool
    current_price: Decimal


class PlacingBidOutputBoundary(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def present(self, output_dto: PlacingBidOutputDto) -> None:
        pass

    @abc.abstractmethod
    def get_presented_data(self) -> dict:
        pass


class PlacingBidUseCase:
    auctions_repo: AuctionsRepository = inject.attr(AuctionsRepository)
    email_gateway: EmailGateway = inject.attr(EmailGateway)

    @inject.params(presenter=PlacingBidOutputBoundary)
    def __init__(self, presenter: PlacingBidOutputBoundary) -> None:
        self.presenter = presenter

    def execute(self, input_dto: PlacingBidInputDto) -> None:
        auction = self.auctions_repo.get(input_dto.auction_id)

        bid = Bid(id=None, bidder_id=input_dto.bidder_id, amount=input_dto.amount)
        auction.make_a_bid(bid)

        self.auctions_repo.save(auction)

        output_dto = PlacingBidOutputDto(
            input_dto.bidder_id in auction.winners, auction.current_price
        )
        self.presenter.present(output_dto)

import abc
from dataclasses import dataclass

import inject

from auctions.application.repositories import AuctionsRepository
from auctions.application.ports import EmailGateway
from auctions.domain.entities import Bid
from auctions.domain.value_objects import Money


@dataclass
class PlacingBidInputDto:
    bidder_id: int
    auction_id: int
    amount: Money


@dataclass
class PlacingBidOutputDto:
    is_winner: bool
    current_price: Money


class PlacingBidOutputBoundary(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def present(self, output_dto: PlacingBidOutputDto) -> None:
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

        if input_dto.bidder_id in auction.winners:
            self.email_gateway.notify_about_winning_auction(auction.id, input_dto.bidder_id)

        output_dto = PlacingBidOutputDto(
            input_dto.bidder_id in auction.winners, auction.current_price
        )
        self.presenter.present(output_dto)

import abc
from dataclasses import dataclass

import inject

from auctions.application.repositories import AuctionsRepository
from auctions.application.ports import EmailGateway
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


class PlacingBid:
    email_gateway: EmailGateway = inject.attr(EmailGateway)

    @inject.autoparams('output_boundary', 'auctions_repo')
    def __init__(self, output_boundary: PlacingBidOutputBoundary, auctions_repo: AuctionsRepository) -> None:
        self.output_boundary = output_boundary
        self.auctions_repo = auctions_repo

    def execute(self, input_dto: PlacingBidInputDto) -> None:
        auction = self.auctions_repo.get(input_dto.auction_id)
        auction.place_bid(bidder_id=input_dto.bidder_id, amount=input_dto.amount)
        self.auctions_repo.save(auction)

        if input_dto.bidder_id in auction.winners:
            self.email_gateway.notify_about_winning_auction(auction.id, input_dto.bidder_id)

        output_dto = PlacingBidOutputDto(
            input_dto.bidder_id in auction.winners, auction.current_price
        )
        self.output_boundary.present(output_dto)

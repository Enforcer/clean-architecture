import abc
from dataclasses import dataclass

from foundation.value_objects import Money

from auctions.application.repositories import AuctionsRepository
from auctions.domain.value_objects import AuctionId, BidderId


@dataclass
class PlacingBidInputDto:
    bidder_id: BidderId
    auction_id: AuctionId
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
    def __init__(self, output_boundary: PlacingBidOutputBoundary, auctions_repo: AuctionsRepository) -> None:
        self.output_boundary = output_boundary
        self.auctions_repo = auctions_repo

    def execute(self, input_dto: PlacingBidInputDto) -> None:
        auction = self.auctions_repo.get(input_dto.auction_id)
        auction.place_bid(bidder_id=input_dto.bidder_id, amount=input_dto.amount)
        self.auctions_repo.save(auction)

        output_dto = PlacingBidOutputDto(input_dto.bidder_id in auction.winners, auction.current_price)
        self.output_boundary.present(output_dto)

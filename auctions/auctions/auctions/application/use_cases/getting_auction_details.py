import abc
from dataclasses import dataclass
from typing import List

import inject

from auctions.application.repositories import AuctionsRepository
from auctions.domain.types import (
    AuctionId,
    BidderId,
)
from auctions.domain.value_objects import Money

BiddersRepository = AuctionsRepository


@dataclass
class GettingAuctionDetailsInputDto:
    auction_id: AuctionId


@dataclass
class TopBidder:
    anonymized_name: str
    bid_amount: Money


@dataclass
class GettingAuctionDetailsOutputDto:
    auction_id: AuctionId
    title: str
    current_price: Money
    starting_price: Money
    top_bidders: List[TopBidder]


class PlacingBidOutputBoundary(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def present(self, output_dto: GettingAuctionDetailsOutputDto) -> None:
        pass


class GettingAuctionDetails:

    @inject.autoparams('output_boundary', 'auctions_repo')
    def __init__(
            self,
            output_boundary: PlacingBidOutputBoundary,
            auctions_repo: AuctionsRepository,
            bidders_repo: BiddersRepository,
    ) -> None:
        self.output_boundary = output_boundary
        self.auctions_repo = auctions_repo
        self.bidders_repo = bidders_repo

    def execute(self, input_dto: GettingAuctionDetailsInputDto) -> None:
        auction = self.auctions_repo.get(input_dto.auction_id)
        top_bids = auction.bids[-3:]

        top_bidders = []
        for bid in top_bids:
            bidder = self.bidders_repo.get(bid.bidder_id)
            anonymized_name = f'{bidder.username[0]}...'
            top_bidders.append(TopBidder(anonymized_name, bid.amount))

        output_dto = GettingAuctionDetailsOutputDto(
            auction_id=auction.id,
            title=auction.title,
            current_price=auction.current_price,
            starting_price=auction.starting_price,
            top_bidders=top_bidders
        )
        self.output_boundary.present(output_dto)

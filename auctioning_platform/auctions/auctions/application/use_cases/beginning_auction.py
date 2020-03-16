from dataclasses import dataclass
from datetime import datetime

from foundation.value_objects import Money

from auctions.application.repositories import AuctionsRepository
from auctions.domain.entities import Auction
from auctions.domain.exceptions import AuctionEndingInThePast
from auctions.domain.value_objects import AuctionId


@dataclass
class BeginningAuctionInputDto:
    auction_id: AuctionId
    title: str
    starting_price: Money
    ends_at: datetime


class BeginningAuction:
    def __init__(self, auctions_repo: AuctionsRepository) -> None:
        self.auctions_repo = auctions_repo

    def execute(self, input_dto: BeginningAuctionInputDto) -> None:
        if input_dto.ends_at < datetime.now(tz=input_dto.ends_at.tzinfo):
            raise AuctionEndingInThePast

        auction = Auction.create(input_dto.auction_id, input_dto.title, input_dto.starting_price, input_dto.ends_at)
        self.auctions_repo.save(auction)

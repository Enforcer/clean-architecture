from dataclasses import dataclass

from auctions.application.repositories import AuctionsRepository
from auctions.domain.value_objects import AuctionId


@dataclass
class EndingAuctionInputDto:
    auction_id: AuctionId


class EndingAuction:
    def __init__(self, auctions_repo: AuctionsRepository) -> None:
        self.auctions_repo = auctions_repo

    def execute(self, input_dto: EndingAuctionInputDto) -> None:
        auction = self.auctions_repo.get(input_dto.auction_id)
        # ???
        self.auctions_repo.save(auction)

from dataclasses import dataclass

from auctions.application.repositories import AuctionsRepository
from auctions.domain.value_objects import AuctionId


@dataclass
class EndingAuctionInputDto:
    auction_id: AuctionId


class EndingAuction:
    def __init__(self, auctions_repo: AuctionsRepository) -> None:
        """
        Initialize a new repo.

        Args:
            self: (todo): write your description
            auctions_repo: (todo): write your description
        """
        self.auctions_repo = auctions_repo

    def execute(self, input_dto: EndingAuctionInputDto) -> None:
        """
        Saves input_dtorepo to saveing

        Args:
            self: (todo): write your description
            input_dto: (todo): write your description
        """
        auction = self.auctions_repo.get(input_dto.auction_id)
        # ???
        self.auctions_repo.save(auction)

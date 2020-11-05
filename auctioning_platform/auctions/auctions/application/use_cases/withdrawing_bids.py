from dataclasses import dataclass
from typing import List

from auctions.application.repositories import AuctionsRepository


@dataclass
class WithdrawingBidsInputDto:
    auction_id: int
    bids_ids: List[int]


class WithdrawingBids:
    def __init__(self, auctions_repo: AuctionsRepository = None) -> None:
        """
        Initialize a new repo.

        Args:
            self: (todo): write your description
            auctions_repo: (todo): write your description
        """
        assert isinstance(auctions_repo, AuctionsRepository)
        self._auctions_repo = auctions_repo

    def execute(self, input_dto: WithdrawingBidsInputDto) -> None:
        """
        Execute all input_dto on input_id.

        Args:
            self: (todo): write your description
            input_dto: (todo): write your description
        """
        auction = self._auctions_repo.get(input_dto.auction_id)
        auction.withdraw_bids(input_dto.bids_ids)
        self._auctions_repo.save(auction)

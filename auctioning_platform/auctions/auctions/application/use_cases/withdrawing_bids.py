from dataclasses import dataclass
from typing import List

from auctions.application.repositories import AuctionsRepository


@dataclass
class WithdrawingBidsInputDto:
    auction_id: int
    bids_ids: List[int]


class WithdrawingBids:
    def __init__(self, auctions_repo: AuctionsRepository = None) -> None:
        assert isinstance(auctions_repo, AuctionsRepository)
        self._auctions_repo = auctions_repo

    def execute(self, input_dto: WithdrawingBidsInputDto) -> None:
        auction = self._auctions_repo.get(input_dto.auction_id)
        auction.withdraw_bids(input_dto.bids_ids)
        self._auctions_repo.save(auction)

from typing import List, NamedTuple

import inject
from dataclasses import dataclass

from auctions.application.ports import EmailGateway
from auctions.application.repositories import AuctionsRepository


@dataclass
class WithdrawingBidsInputDto:
    auction_id: int
    bids_ids: List[int]


class WithdrawingBids:
    auctions_repo: AuctionsRepository = inject.attr(AuctionsRepository)
    email_gateway: EmailGateway = inject.attr(EmailGateway)

    def execute(self, input_dto: WithdrawingBidsInputDto) -> None:
        auction = self.auctions_repo.get(input_dto.auction_id)

        old_winners = set(auction.winners)
        auction.withdraw_bids(input_dto.bids_ids)
        actual_winners = set(auction.winners)

        new_winners = actual_winners - old_winners
        for winner_id in new_winners:
            self.email_gateway.notify_about_winning_auction(auction.id, winner_id)
        self.auctions_repo.save(auction)

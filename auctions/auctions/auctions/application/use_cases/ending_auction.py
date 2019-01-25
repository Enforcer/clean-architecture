from dataclasses import dataclass

import inject

from auctions.application.ports import PaymentProvider
from auctions.application.repositories import AuctionsRepository
from auctions.domain.types import AuctionId


@dataclass
class EndingAuctionInputDto:
    auction_id: AuctionId


class EndingAuction:

    @inject.autoparams('auctions_repo', 'payment_provider')
    def __init__(self, auctions_repo: AuctionsRepository, payment_provider: PaymentProvider) -> None:
        self.auctions_repo = auctions_repo
        self.payment_provider = payment_provider

    def execute(self, input_dto: EndingAuctionInputDto) -> None:
        auction = self.auctions_repo.get(input_dto.auction_id)
        # ???
        self.auctions_repo.save(auction)

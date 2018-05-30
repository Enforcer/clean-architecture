import inject

from auctions.application.interfaces import EmailGateway
from auctions.application.repositories import AuctionsRepository
from auctions.models import Auction, Bid


class WithdrawingBidsUseCase:
    auctions_repo: AuctionsRepository = inject.attr(AuctionsRepository)
    email_gateway: EmailGateway = inject.attr(EmailGateway)

    def withdraw_bids(self, auction_id, bids_ids):
        auction = self.auctions_repo.get(auction_id)

        old_winners = set(auction.winners)
        auction.withdraw_bids(bids_ids)
        actual_winners = set(auction.winners)

        new_winners = actual_winners - old_winners
        for winner in new_winners:
            self.email_gateway.notify_about_winning_auction(auction.id, winner)
        self.auctions_repo.save(auction)

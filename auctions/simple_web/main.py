import inject

from auctions.application.repositories import AuctionsRepository
from auctions.domain.entities import Auction
from auctions.domain.factories import get_dollars
from auctions_infrastructure.repositories.auctions import InMemoryAuctionsRepository


def setup_dependency_injection():
    def di_config(binder: inject.Binder) -> None:
        binder.bind(AuctionsRepository, InMemoryAuctionsRepository([
            Auction(id=1, title='Exemplary auction', starting_price=get_dollars('12.99'), bids=[])
        ]))

    inject.configure(di_config)


def setup():
    setup_dependency_injection()

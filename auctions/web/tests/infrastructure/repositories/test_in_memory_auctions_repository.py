from auctions.domain.entities import (
    Auction,
    Bid,
)
from auctions.domain.factories import get_dollars
from web.infrastructure.repositories import InMemoryAuctionsRepository


def test_should_get_back_saved_auction():
    bids = [Bid(id=1, bidder_id=1, amount=get_dollars('15.99'))]
    auction = Auction(id=1, title='Awesome book', starting_price=get_dollars('9.99'), bids=bids)
    repo = InMemoryAuctionsRepository()

    repo.save(auction)

    assert repo.get(auction.id) == auction

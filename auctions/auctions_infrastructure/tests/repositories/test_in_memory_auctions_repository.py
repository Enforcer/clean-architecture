from datetime import datetime
from unittest.mock import Mock

import pytest

from auctions.domain.entities import Auction, Bid
from auctions.domain.value_objects import Money
from auctions.domain.factories import get_dollars
from auctions_infrastructure.repositories import InMemoryAuctionsRepository


@pytest.fixture()
def winning_bid_amount() -> Money:
    return get_dollars("15.99")


@pytest.fixture()
def auction_with_a_bid(winning_bid_amount: Money, ends_at: datetime) -> Auction:
    bids = [Bid(id=1, bidder_id=1, amount=winning_bid_amount)]
    return Auction(id=1, title="Awesome book", starting_price=get_dollars("9.99"), bids=bids, ends_at=ends_at)


def test_should_get_back_saved_auction(auction_with_a_bid: Auction, event_bus_mock: Mock) -> None:
    repo = InMemoryAuctionsRepository(event_bus=event_bus_mock)

    repo.save(auction_with_a_bid)

    assert repo.get(auction_with_a_bid.id) == auction_with_a_bid


def test_gets_existing_auction(auction_with_a_bid: Auction, winning_bid_amount: Money, event_bus_mock: Mock) -> None:
    auction = InMemoryAuctionsRepository([auction_with_a_bid], event_bus_mock).get(auction_with_a_bid.id)

    assert auction == auction_with_a_bid


def test_saves_auction_changes(auction_with_a_bid: Auction, ends_at: datetime, event_bus_mock: Mock) -> None:
    the_only_bid = auction_with_a_bid.bids[0]
    auction = Auction(
        id=auction_with_a_bid.id,
        title=auction_with_a_bid.title,
        starting_price=auction_with_a_bid.starting_price,
        ends_at=ends_at,
        bids=[the_only_bid, Bid(id=None, bidder_id=2, amount=the_only_bid.amount + get_dollars("1.00"))],
    )

    repo = InMemoryAuctionsRepository([auction_with_a_bid], event_bus_mock)
    repo.save(auction)

    assert len(repo.get(auction_with_a_bid.id).bids) == 2


def test_removes_withdrawn_bids(auction_with_a_bid: Auction, ends_at: datetime, event_bus_mock: Mock) -> None:
    the_only_bid = auction_with_a_bid.bids[0]
    auction = Auction(
        id=auction_with_a_bid.id,
        title=auction_with_a_bid.title,
        starting_price=auction_with_a_bid.starting_price,
        bids=[the_only_bid],
        ends_at=ends_at,
    )
    auction.withdraw_bids([the_only_bid.id])

    repo = InMemoryAuctionsRepository([auction_with_a_bid], event_bus_mock)
    repo.save(auction)

    assert len(repo.get(auction_with_a_bid.id).bids) == 0


def test_posts_pending_domain_events(auction_with_a_bid: Auction, event_bus_mock: Mock) -> None:
    repo = InMemoryAuctionsRepository([auction_with_a_bid], event_bus_mock)
    auction_with_a_bid.place_bid(1, auction_with_a_bid.current_price + get_dollars("1.00"))

    repo.save(auction_with_a_bid)

    event_bus_mock.post.assert_called()

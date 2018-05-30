from decimal import Decimal

from auctions.domain.entities import (
    Auction,
    Bid,
)


def test_should_return_no_winners_for_empty_bids_list():
    auction = Auction(id=1, initial_price=Decimal('10'), bids=[])

    assert auction.winners == []


def test_should_return_highest_bids_user_id_for_winners_list():
    auction = Auction(id=1, initial_price=Decimal('10'), bids=[
        Bid(user_id=1, amount=Decimal('101')),
        Bid(user_id=2, amount=Decimal('15')),
        Bid(user_id=3, amount=Decimal('100')),
    ])

    assert auction.winners == [1]

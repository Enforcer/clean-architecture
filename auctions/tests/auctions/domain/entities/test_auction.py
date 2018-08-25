import typing
from decimal import Decimal

from auctions.domain.entities import (
    Auction,
    Bid,
)


def create_auction(bids: typing.List[Bid] = None) -> Auction:
    if not bids:
        bids = []

    return Auction(id=1, title='', initial_price=Decimal('10'), bids=bids)


def test_should_use_initial_price_as_current_price_for_empty_bids_list():
    auction = create_auction()

    assert auction.current_price == auction.initial_price


def test_should_return_highest_bid_for_current_price():
    auction = create_auction(bids=[
        Bid(id=1, bidder_id=1, amount=Decimal('20')),
        Bid(id=2, bidder_id=2, amount=Decimal('15')),
    ])

    assert auction.current_price == Decimal('20')


def test_should_return_no_winners_for_empty_bids_list():
    auction = create_auction()

    assert auction.winners == []


def test_should_return_highest_bids_user_id_for_winners_list():
    auction = create_auction(bids=[
        Bid(id=1, bidder_id=1, amount=Decimal('101')),
        Bid(id=2, bidder_id=2, amount=Decimal('15')),
        Bid(id=3, bidder_id=3, amount=Decimal('100')),
    ])

    assert auction.winners == [1]


def test_should_win_auction_if_is_the_only_bidder_above_initial_price():
    auction = create_auction()

    auction.make_a_bid(Bid(id=None, bidder_id=1, amount=Decimal('11')))

    assert auction.winners == [1]


def test_should_not_be_winning_auction_if_bids_below_initial_price():
    auction = create_auction()

    auction.make_a_bid(Bid(id=None, bidder_id=1, amount=Decimal('5')))

    assert auction.winners == []


def test_should_withdraw_the_only_bid():
    auction = create_auction(bids=[
        Bid(id=1, bidder_id=1, amount=Decimal('50'))
    ])

    auction.withdraw_bids([1])

    assert auction.winners == []
    assert auction.current_price == auction.initial_price


def test_should_add_withdrawn_bids_ids_to_separate_list():
    auction = create_auction(bids=[
        Bid(id=1, bidder_id=1, amount=Decimal('50'))
    ])

    auction.withdraw_bids([1])

    assert auction.withdrawn_bids_ids == [1]


def test_should_not_be_winning_if_bid_lower_than_current_price() -> None:
    auction = create_auction(bids=[
        Bid(id=1, bidder_id=1, amount=Decimal('10.00'))
    ])

    lower_bid = Bid(id=None, bidder_id=2, amount=Decimal('5.00'))
    auction.make_a_bid(lower_bid)

    assert lower_bid.bidder_id not in auction.winners

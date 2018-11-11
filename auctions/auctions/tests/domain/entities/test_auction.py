from datetime import (
    datetime,
    timedelta,
)
from typing import List

from auctions.domain.entities import (
    Auction,
    Bid,
)
from auctions.domain.factories import get_dollars


def create_auction(bids: List[Bid] = None) -> Auction:
    if not bids:
        bids = []

    ends_at = datetime.now() + timedelta(days=1)
    return Auction(id=1, title='', starting_price=get_dollars('10'), bids=bids, ends_at=ends_at)


def test_should_use_starting_price_as_current_price_for_empty_bids_list():
    auction = create_auction()

    assert auction.current_price == auction.starting_price


def test_should_return_highest_bid_for_current_price():
    auction = create_auction(bids=[
        Bid(id=1, bidder_id=1, amount=get_dollars('20')),
        Bid(id=2, bidder_id=2, amount=get_dollars('15')),
    ])

    assert auction.current_price == get_dollars('20')


def test_should_return_no_winners_for_empty_bids_list():
    auction = create_auction()

    assert auction.winners == []


def test_should_return_highest_bids_user_id_for_winners_list():
    auction = create_auction(bids=[
        Bid(id=1, bidder_id=1, amount=get_dollars('101')),
        Bid(id=2, bidder_id=2, amount=get_dollars('15')),
        Bid(id=3, bidder_id=3, amount=get_dollars('100')),
    ])

    assert auction.winners == [1]


def test_should_win_auction_if_is_the_only_bidder_above_starting_price():
    auction = create_auction()

    auction.place_bid(bidder_id=1, amount=get_dollars('11'))

    assert auction.winners == [1]


def test_should_not_be_winning_auction_if_bids_below_starting_price():
    auction = create_auction()

    auction.place_bid(bidder_id=1, amount=get_dollars('5'))

    assert auction.winners == []


def test_should_withdraw_the_only_bid():
    auction = create_auction(bids=[
        Bid(id=1, bidder_id=1, amount=get_dollars('50'))
    ])

    auction.withdraw_bids([1])

    assert auction.winners == []
    assert auction.current_price == auction.starting_price


def test_should_add_withdrawn_bids_ids_to_separate_list():
    auction = create_auction(bids=[
        Bid(id=1, bidder_id=1, amount=get_dollars('50'))
    ])

    auction.withdraw_bids([1])

    assert auction.withdrawn_bids_ids == [1]


def test_should_not_be_winning_if_bid_lower_than_current_price() -> None:
    auction = create_auction(bids=[
        Bid(id=1, bidder_id=1, amount=get_dollars('10.00'))
    ])

    lower_bid_bidder_id = 2
    auction.place_bid(bidder_id=lower_bid_bidder_id, amount=get_dollars('5.00'))

    assert lower_bid_bidder_id not in auction.winners

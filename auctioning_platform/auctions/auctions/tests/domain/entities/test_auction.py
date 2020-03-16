from datetime import datetime, timedelta

import pytest

from foundation.value_objects.factories import get_dollars

from auctions.domain.entities import Bid
from auctions.domain.events import AuctionEnded, BidderHasBeenOverbid, WinningBidPlaced
from auctions.domain.exceptions import AuctionAlreadyEnded, AuctionHasNotEnded, BidOnEndedAuction
from auctions.tests.factories import AuctionFactory


@pytest.fixture()
def yesterday() -> datetime:
    return datetime.now() - timedelta(days=1)


def test_should_use_starting_price_as_current_price_for_empty_bids_list() -> None:
    auction = AuctionFactory()

    assert auction.current_price == auction.starting_price


def test_should_return_highest_bid_for_current_price() -> None:
    auction = AuctionFactory(
        bids=[Bid(id=1, bidder_id=1, amount=get_dollars("20")), Bid(id=2, bidder_id=2, amount=get_dollars("15"))]
    )

    assert auction.current_price == get_dollars("20")


def test_should_return_no_winners_for_empty_bids_list() -> None:
    auction = AuctionFactory()

    assert auction.winners == []


def test_should_return_highest_bids_user_id_for_winners_list() -> None:
    auction = AuctionFactory(
        bids=[
            Bid(id=1, bidder_id=1, amount=get_dollars("101")),
            Bid(id=2, bidder_id=2, amount=get_dollars("15")),
            Bid(id=3, bidder_id=3, amount=get_dollars("100")),
        ]
    )

    assert auction.winners == [1]


def test_should_win_auction_if_is_the_only_bidder_above_starting_price() -> None:
    auction = AuctionFactory()

    auction.place_bid(bidder_id=1, amount=get_dollars("11"))

    assert auction.winners == [1]


def test_should_not_be_winning_auction_if_bids_below_starting_price() -> None:
    auction = AuctionFactory()

    auction.place_bid(bidder_id=1, amount=get_dollars("5"))

    assert auction.winners == []


def test_should_withdraw_the_only_bid() -> None:
    auction = AuctionFactory(bids=[Bid(id=1, bidder_id=1, amount=get_dollars("50"))])

    auction.withdraw_bids([1])

    assert auction.winners == []
    assert auction.current_price == auction.starting_price


def test_should_add_withdrawn_bids_ids_to_separate_list() -> None:
    auction = AuctionFactory(bids=[Bid(id=1, bidder_id=1, amount=get_dollars("50"))])

    auction.withdraw_bids([1])

    assert auction.withdrawn_bids_ids == [1]


def test_should_not_be_winning_if_bid_lower_than_current_price() -> None:
    auction = AuctionFactory(bids=[Bid(id=1, bidder_id=1, amount=get_dollars("10.00"))])

    lower_bid_bidder_id = 2
    auction.place_bid(bidder_id=lower_bid_bidder_id, amount=get_dollars("5.00"))

    assert lower_bid_bidder_id not in auction.winners


def test_should_not_allow_placing_bids_for_ended_auction(yesterday: datetime) -> None:
    auction = AuctionFactory(ends_at=yesterday)

    with pytest.raises(BidOnEndedAuction):
        auction.place_bid(bidder_id=1, amount=auction.current_price + get_dollars("1.00"))


def test_should_emit_event_upon_overbid() -> None:
    bid_that_will_lose = Bid(id=1, bidder_id=1, amount=get_dollars("15.00"))
    auction = AuctionFactory(bids=[bid_that_will_lose])

    new_bid_amount = get_dollars("20.00")
    auction.place_bid(bidder_id=2, amount=new_bid_amount)

    expected_event = BidderHasBeenOverbid(auction.id, bid_that_will_lose.bidder_id, new_bid_amount, auction.title)
    assert expected_event in auction.domain_events


def test_should_emit_winning_event_if_the_first_offer() -> None:
    auction = AuctionFactory()
    winning_amount = auction.current_price + get_dollars("1.00")

    auction.place_bid(bidder_id=1, amount=winning_amount)

    assert auction.domain_events == [WinningBidPlaced(auction.id, 1, winning_amount, auction.title)]


def test_should_emit_winning_if_overbids() -> None:
    auction = AuctionFactory(bids=[Bid(id=1, bidder_id=1, amount=get_dollars("15.00"))])
    winning_amount = auction.current_price + get_dollars("1.00")

    auction.place_bid(bidder_id=2, amount=winning_amount)

    expected_winning_event = WinningBidPlaced(auction.id, 2, winning_amount, auction.title)
    expected_overbid_event = BidderHasBeenOverbid(auction.id, 1, winning_amount, auction.title)
    assert auction.domain_events == [expected_winning_event, expected_overbid_event]


def test_should_emit_auction_ended(yesterday: datetime) -> None:
    auction = AuctionFactory(bids=[Bid(id=1, bidder_id=1, amount=get_dollars("15.00"))], ends_at=yesterday)

    auction.end_auction()

    expected_event = AuctionEnded(auction.id, auction.winners[0], auction.current_price, auction.title)
    assert auction.domain_events == [expected_event]


def test_should_emit_event_with_none_winner_if_no_winners(yesterday: datetime) -> None:
    auction = AuctionFactory(ends_at=yesterday)

    auction.end_auction()

    expected_event = AuctionEnded(auction.id, None, auction.current_price, auction.title)
    assert auction.domain_events == [expected_event]


def test_should_raise_if_auction_has_not_been_ended() -> None:
    auction = AuctionFactory()

    with pytest.raises(AuctionHasNotEnded):
        auction.end_auction()


def test_EndedAuction_PlacingBid_RaisesException(yesterday: datetime) -> None:
    auction = AuctionFactory(ends_at=yesterday)
    auction.end_auction()

    with pytest.raises(BidOnEndedAuction):
        auction.place_bid(bidder_id=1, amount=get_dollars("19.99"))


def test_EndedAuction_Ending_RaisesException(yesterday: datetime) -> None:
    auction = AuctionFactory(ends_at=yesterday)
    auction.end_auction()

    with pytest.raises(AuctionAlreadyEnded):
        auction.end_auction()

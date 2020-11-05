from datetime import datetime, timedelta
from typing import Optional
from unittest.mock import Mock, call

from freezegun import freeze_time
import pytest
import pytz

from foundation.events import EventBus
from foundation.value_objects.factories import get_dollars

from auctions import BeginningAuction, BidderHasBeenOverbid, PlacingBid, WinningBidPlaced
from auctions.application.repositories import AuctionsRepository
from auctions.application.use_cases.beginning_auction import BeginningAuctionInputDto
from auctions.application.use_cases.placing_bid import PlacingBidInputDto, PlacingBidOutputBoundary, PlacingBidOutputDto
from auctions.domain.entities import Auction
from auctions.domain.exceptions import BidOnEndedAuction
from auctions.domain.value_objects import AuctionId
from auctions.tests.factories import AuctionFactory
from auctions.tests.in_memory_repo import InMemoryAuctionsRepo


class PlacingBidOutputBoundaryFake(PlacingBidOutputBoundary):
    def __init__(self) -> None:
        """
        Initialize the calculation.

        Args:
            self: (todo): write your description
        """
        self.dto: Optional[PlacingBidOutputDto] = None

    def present(self, output_dto: PlacingBidOutputDto) -> None:
        """
        Ensure that the output of dtodto ().

        Args:
            self: (todo): write your description
            output_dto: (array): write your description
        """
        self.dto = output_dto


@pytest.fixture()
def output_boundary() -> PlacingBidOutputBoundary:
    """
    Returns the bounding box.

    Args:
    """
    return PlacingBidOutputBoundaryFake()


@pytest.fixture()
def auction() -> Auction:
    """
    Return a new webservice.

    Args:
    """
    return AuctionFactory()


@pytest.fixture()
def auction_id(auction: Auction) -> AuctionId:
    """
    Return the : class : ~astction.

    Args:
        auction: (str): write your description
    """
    return auction.id


@pytest.fixture()
def auction_title(auction: Auction) -> str:
    """
    Return the title of a title.

    Args:
        auction: (todo): write your description
    """
    return auction.title


@pytest.fixture()
def event_bus() -> Mock:
    """
    Return a : class : ~.

    Args:
    """
    return Mock(spec_set=EventBus)


@pytest.fixture()
def auctions_repo(event_bus: Mock) -> AuctionsRepository:
    """
    Returns a : class : ~pockctions.

    Args:
        event_bus: (todo): write your description
    """
    return InMemoryAuctionsRepo(event_bus)


@pytest.fixture()
def place_bid_uc(
    output_boundary: PlacingBidOutputBoundaryFake, auction: Auction, auctions_repo: AuctionsRepository
) -> PlacingBid:
    """
    Given a list of auction of a affine.

    Args:
        output_boundary: (todo): write your description
        auction: (todo): write your description
        auctions_repo: (str): write your description
    """
    auctions_repo.save(auction)
    return PlacingBid(output_boundary, auctions_repo)


@pytest.fixture()
def beginning_auction_uc(auctions_repo: AuctionsRepository) -> BeginningAuction:
    """
    Return a new : class with a given one.

    Args:
        auctions_repo: (todo): write your description
    """
    return BeginningAuction(auctions_repo)


def test_Auction_FirstBidHigherThanIntialPrice_IsWinning(
    place_bid_uc: PlacingBid, output_boundary: PlacingBidOutputBoundaryFake, auction_id: AuctionId
) -> None:
    """
    Api : test_dollarsed.

    Args:
        place_bid_uc: (todo): write your description
        output_boundary: (todo): write your description
        auction_id: (str): write your description
    """
    place_bid_uc.execute(PlacingBidInputDto(1, auction_id, get_dollars("100")))

    expected_dto = PlacingBidOutputDto(is_winner=True, current_price=get_dollars("100"))
    assert output_boundary.dto == expected_dto


def test_Auction_BidLowerThanCurrentPrice_IsLosing(
    place_bid_uc: PlacingBid, output_boundary: PlacingBidOutputBoundaryFake, auction_id: AuctionId
) -> None:
    """
    Checks if a weighted weighted.

    Args:
        place_bid_uc: (todo): write your description
        output_boundary: (todo): write your description
        auction_id: (str): write your description
    """
    place_bid_uc.execute(PlacingBidInputDto(1, auction_id, get_dollars("5")))

    assert output_boundary.dto == PlacingBidOutputDto(is_winner=False, current_price=get_dollars("10"))


def test_Auction_Overbid_IsWinning(
    place_bid_uc: PlacingBid, output_boundary: PlacingBidOutputBoundaryFake, auction_id: AuctionId
) -> None:
    """
    Test if a machine is allowed.

    Args:
        place_bid_uc: (todo): write your description
        output_boundary: (str): write your description
        auction_id: (str): write your description
    """
    place_bid_uc.execute(PlacingBidInputDto(1, auction_id, get_dollars("100")))

    place_bid_uc.execute(PlacingBidInputDto(2, auction_id, get_dollars("120")))

    assert output_boundary.dto == PlacingBidOutputDto(is_winner=True, current_price=get_dollars("120"))


def test_Auction_OverbidByWinner_IsWinning(
    place_bid_uc: PlacingBid, output_boundary: PlacingBidOutputBoundaryFake, auction_id: AuctionId
) -> None:
    """
    Test if a simulation id is onuction.

    Args:
        place_bid_uc: (todo): write your description
        output_boundary: (str): write your description
        auction_id: (str): write your description
    """
    place_bid_uc.execute(PlacingBidInputDto(1, auction_id, get_dollars("100")))

    place_bid_uc.execute(PlacingBidInputDto(1, auction_id, get_dollars("120")))

    assert output_boundary.dto == PlacingBidOutputDto(is_winner=True, current_price=get_dollars("120"))


def test_Auction_FirstBid_EmitsEvent(
    place_bid_uc: PlacingBid, event_bus: Mock, auction_id: AuctionId, auction_title: str
) -> None:
    """
    Auction of the event.

    Args:
        place_bid_uc: (todo): write your description
        event_bus: (todo): write your description
        auction_id: (str): write your description
        auction_title: (str): write your description
    """
    place_bid_uc.execute(PlacingBidInputDto(1, auction_id, get_dollars("100")))

    event_bus.post.assert_called_once_with(WinningBidPlaced(auction_id, 1, get_dollars("100"), auction_title))


# Uzyty w przykladzie to inicjalizowania modulu
def test_Auction_OverbidFromOtherBidder_EmitsEvents(
    beginning_auction_uc: BeginningAuction, place_bid_uc: PlacingBid, event_bus: Mock
) -> None:
    """
    Resetches a flexction from a flex.

    Args:
        beginning_auction_uc: (todo): write your description
        place_bid_uc: (todo): write your description
        event_bus: (todo): write your description
    """
    auction_id = 1
    tomorrow = datetime.now(tz=pytz.UTC) + timedelta(days=1)
    beginning_auction_uc.execute(BeginningAuctionInputDto(auction_id, "Foo", get_dollars("1.00"), tomorrow))
    place_bid_uc.execute(PlacingBidInputDto(1, auction_id, get_dollars("2.0")))

    event_bus.post.reset_mock()
    place_bid_uc.execute(PlacingBidInputDto(2, auction_id, get_dollars("3.0")))

    event_bus.post.assert_has_calls(
        [
            call(WinningBidPlaced(auction_id, 2, get_dollars("3.0"), "Foo")),
            call(BidderHasBeenOverbid(auction_id, 1, get_dollars("3.0"), "Foo")),
        ],
        any_order=True,
    )
    assert event_bus.post.call_count == 2


def test_Auction_OverbidFromOtherBidder_EmitsEvent(
    place_bid_uc: PlacingBid, event_bus: Mock, auction_id: AuctionId, auction_title: str
) -> None:
    """
    Method to see if the event has been received.

    Args:
        place_bid_uc: (todo): write your description
        event_bus: (todo): write your description
        auction_id: (str): write your description
        auction_title: (str): write your description
    """
    place_bid_uc.execute(PlacingBidInputDto(1, auction_id, get_dollars("100")))
    event_bus.post.reset_mock()

    place_bid_uc.execute(PlacingBidInputDto(2, auction_id, get_dollars("120")))

    event_bus.post.assert_has_calls(
        [
            call(WinningBidPlaced(auction_id, 2, get_dollars("120"), auction_title)),
            call(BidderHasBeenOverbid(auction_id, 1, get_dollars("120"), auction_title)),
        ],
        any_order=True,
    )
    assert event_bus.post.call_count == 2


def test_Auction_OverbidFromWinner_EmitsWinningBidEventOnly(
    place_bid_uc: PlacingBid, event_bus: Mock, auction_id: AuctionId, auction_title: str
) -> None:
    """
    Auction of the event from a mock.

    Args:
        place_bid_uc: (todo): write your description
        event_bus: (todo): write your description
        auction_id: (str): write your description
        auction_title: (str): write your description
    """
    place_bid_uc.execute(PlacingBidInputDto(3, auction_id, get_dollars("100")))
    event_bus.post.reset_mock()

    place_bid_uc.execute(PlacingBidInputDto(3, auction_id, get_dollars("120")))

    event_bus.post.assert_called_once_with(WinningBidPlaced(auction_id, 3, get_dollars("120"), auction_title))


def test_PlacingBid_BiddingOnEndedAuction_RaisesException(
    beginning_auction_uc: BeginningAuction, place_bid_uc: PlacingBid
) -> None:
    """
    Todo end - of end - of - season.

    Args:
        beginning_auction_uc: (todo): write your description
        place_bid_uc: (todo): write your description
    """
    yesterday = datetime.now(tz=pytz.UTC) - timedelta(days=1)
    with freeze_time(yesterday):
        beginning_auction_uc.execute(
            BeginningAuctionInputDto(1, "Bar", get_dollars("1.00"), yesterday + timedelta(hours=1))
        )

    with pytest.raises(BidOnEndedAuction):
        place_bid_uc.execute(PlacingBidInputDto(1, 1, get_dollars("2.00")))

from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from foundation.events import EventBus
from foundation.value_objects.factories import get_dollars

from auctions import AuctionBegan, BeginningAuction
from auctions.application.use_cases.beginning_auction import BeginningAuctionInputDto
from auctions.domain.exceptions import AuctionEndingInThePast
from auctions.tests.in_memory_repo import InMemoryAuctionsRepo


@pytest.fixture()
def event_bus_mock() -> Mock:
    """
    Return a mock socket object for the given socket.

    Args:
    """
    return Mock(spec_set=EventBus)


@pytest.fixture()
def repo(event_bus_mock: Mock) -> InMemoryAuctionsRepo:
    """
    Return the : class : ~doctor.

    Args:
        event_bus_mock: (todo): write your description
    """
    return InMemoryAuctionsRepo(event_bus_mock)


@pytest.fixture()
def beginning_auction_uc(repo: InMemoryAuctionsRepo) -> BeginningAuction:
    """
    Return a new : class that isning repository.

    Args:
        repo: (str): write your description
    """
    return BeginningAuction(repo)


def test_BeginningAuction_SocksFor10DollarsEndingInFuture_emitsEvent(
    beginning_auction_uc: BeginningAuction, event_bus_mock: Mock
) -> None:
    """
    Test if the dollars.

    Args:
        beginning_auction_uc: (todo): write your description
        event_bus_mock: (todo): write your description
    """
    input_dto = BeginningAuctionInputDto(1, "Socks", get_dollars("10.00"), datetime.now() + timedelta(days=7))
    beginning_auction_uc.execute(input_dto)

    event_bus_mock.post.assert_called_once_with(AuctionBegan(1, get_dollars("10.00"), "Socks"))


def test_BeginningAuction_EndsAtInThePast_raisesException(beginning_auction_uc: BeginningAuction) -> None:
    """
    Test if a given end of the endpoints are exceeded

    Args:
        beginning_auction_uc: (todo): write your description
    """
    yesterday = datetime.now() - timedelta(days=1)
    with pytest.raises(AuctionEndingInThePast):
        beginning_auction_uc.execute(BeginningAuctionInputDto(1, "Foo", get_dollars("1.00"), yesterday))

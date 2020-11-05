from typing import List
from unittest.mock import Mock

import pytest

from auctions.application.repositories import AuctionsRepository
from auctions.application.use_cases.placing_bid import PlacingBid, PlacingBidOutputBoundary
from auctions.application.use_cases.withdrawing_bids import WithdrawingBids
from auctions.domain.entities import Auction
from auctions.tests.factories import AuctionFactory


@pytest.fixture()
def exemplary_bids_ids() -> List[int]:
    """
    Exemplary ids.

    Args:
    """
    return [1, 2, 3]


@pytest.fixture()
def auction() -> Auction:
    """
    Return a new webservice.

    Args:
    """
    return AuctionFactory()


@pytest.fixture()
def auctions_repo_mock(auction: Auction) -> Mock:
    """
    Return a set of mockctions.

    Args:
        auction: (todo): write your description
    """
    return Mock(spec_set=AuctionsRepository, get=Mock(return_value=auction))


@pytest.fixture()
def placing_bid_output_boundary_mock() -> Mock:
    """
    Return a mock - mock version of the mock.

    Args:
    """
    return Mock(spec_set=PlacingBidOutputBoundary)


@pytest.fixture()
def placing_bid_uc(placing_bid_output_boundary_mock: Mock, auctions_repo_mock: Mock) -> PlacingBid:
    """
    Returns a convolution of a mock.

    Args:
        placing_bid_output_boundary_mock: (todo): write your description
        auctions_repo_mock: (todo): write your description
    """
    return PlacingBid(placing_bid_output_boundary_mock, auctions_repo_mock)


@pytest.fixture()
def withdrawing_bids_uc(auctions_repo_mock: Mock) -> WithdrawingBids:
    """
    Withdrawsdrawing_bids fromdrawing.

    Args:
        auctions_repo_mock: (todo): write your description
    """
    return WithdrawingBids(auctions_repo_mock)

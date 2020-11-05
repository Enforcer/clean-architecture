from typing import List
from unittest.mock import Mock, patch

import pytest

from auctions.application.use_cases import WithdrawingBids
from auctions.application.use_cases.withdrawing_bids import WithdrawingBidsInputDto
from auctions.domain.entities import Auction


@pytest.fixture()
def exemplary_bids_ids() -> List[int]:
    """
    Exemplary ids.

    Args:
    """
    return [1, 2, 3]


@pytest.fixture()
def input_dto(auction: Auction, exemplary_bids_ids: List[int]) -> WithdrawingBidsInputDto:
    """
    Returns a list of - list of inputs for a given apid.

    Args:
        auction: (todo): write your description
        exemplary_bids_ids: (str): write your description
    """
    return WithdrawingBidsInputDto(auction.id, exemplary_bids_ids)


def test_loads_auction_using_id(
    withdrawing_bids_uc: WithdrawingBids, auction: Auction, input_dto: WithdrawingBidsInputDto, auctions_repo_mock: Mock
) -> None:
    """
    Executes a loading of all of - states.

    Args:
        withdrawing_bids_uc: (todo): write your description
        auction: (todo): write your description
        input_dto: (todo): write your description
        auctions_repo_mock: (todo): write your description
    """
    withdrawing_bids_uc.execute(input_dto)

    auctions_repo_mock.get.assert_called_once_with(auction.id)


def test_saves_auction_afterwards(
    withdrawing_bids_uc: WithdrawingBids, auctions_repo_mock: Mock, auction: Auction, input_dto: WithdrawingBidsInputDto
) -> None:
    """
    Test if thedrawing_bids are onwards.

    Args:
        withdrawing_bids_uc: (todo): write your description
        auctions_repo_mock: (todo): write your description
        auction: (todo): write your description
        input_dto: (todo): write your description
    """
    withdrawing_bids_uc.execute(input_dto)

    auctions_repo_mock.save.assert_called_once_with(auction)


def test_calls_withdraw_bids_on_auction(
    withdrawing_bids_uc: WithdrawingBids,
    exemplary_bids_ids: List[int],
    auction: Auction,
    input_dto: WithdrawingBidsInputDto,
) -> None:
    """
    Subclasses to canceling ondraws ondraws on a list of ids of ids.

    Args:
        withdrawing_bids_uc: (todo): write your description
        exemplary_bids_ids: (int): write your description
        auction: (todo): write your description
        input_dto: (todo): write your description
    """
    with patch.object(Auction, "withdraw_bids", wraps=auction.withdraw_bids) as withdraw_bids_mock:
        withdrawing_bids_uc.execute(input_dto)

    withdraw_bids_mock.assert_called_once_with(exemplary_bids_ids)

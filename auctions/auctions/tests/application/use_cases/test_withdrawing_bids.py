from typing import List
from unittest.mock import Mock, patch

import pytest

from foundation.value_objects.factories import get_dollars

from auctions.application.use_cases import WithdrawingBids
from auctions.application.use_cases.withdrawing_bids import WithdrawingBidsInputDto
from auctions.domain.entities import Auction, Bid

from ...factories import create_auction


@pytest.fixture()
def exemplary_bids_ids() -> List[int]:
    return [1, 2, 3]


@pytest.fixture()
def input_dto(auction: Auction, exemplary_bids_ids: List[int]) -> WithdrawingBidsInputDto:
    return WithdrawingBidsInputDto(auction.id, exemplary_bids_ids)


def test_loads_auction_using_id(auction: Auction, input_dto: WithdrawingBidsInputDto, auctions_repo_mock: Mock) -> None:
    WithdrawingBids().execute(input_dto)

    auctions_repo_mock.get.assert_called_once_with(auction.id)


def test_saves_auction_afterwards(auctions_repo_mock: Mock, auction, input_dto: WithdrawingBidsInputDto) -> None:
    WithdrawingBids().execute(input_dto)

    auctions_repo_mock.save.assert_called_once_with(auction)


def test_calls_withdraw_bids_on_auction(
    exemplary_bids_ids: List[int], auction: Auction, input_dto: WithdrawingBidsInputDto
) -> None:
    with patch.object(Auction, "withdraw_bids", wraps=auction.withdraw_bids) as withdraw_bids_mock:
        WithdrawingBids().execute(input_dto)

    withdraw_bids_mock.assert_called_once_with(exemplary_bids_ids)


@pytest.fixture()
def auction_with_a_winner(input_dto: WithdrawingBidsInputDto) -> Auction:
    losing_bid = Bid(id=4, bidder_id=2, amount=get_dollars("10.50"))
    winning_bid = Bid(id=2, bidder_id=1, amount=get_dollars("11.00"))
    bids = [winning_bid, losing_bid]
    return create_auction(auction_id=2, bids=bids)

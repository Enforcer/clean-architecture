from datetime import (
    datetime,
    timedelta,
)
from typing import List
from unittest.mock import (
    Mock,
    patch,
)

import pytest

from auctions.application.use_cases import WithdrawingBids
from auctions.application.use_cases.withdrawing_bids import WithdrawingBidsInputDto
from auctions.domain.entities import (
    Auction,
    Bid,
)
from auctions.domain.factories import get_dollars


@pytest.fixture()
def exemplary_bids_ids() -> List[int]:
    return [1, 2, 3]


@pytest.fixture()
def input_dto(exemplary_auction_id: int, exemplary_bids_ids: List[int]) -> WithdrawingBidsInputDto:
    return WithdrawingBidsInputDto(exemplary_auction_id, exemplary_bids_ids)


def test_loads_auction_using_id(
        exemplary_auction_id: int,
        input_dto: WithdrawingBidsInputDto,
        auctions_repo_mock: Mock
) -> None:
    WithdrawingBids().execute(input_dto)

    auctions_repo_mock.get.assert_called_once_with(exemplary_auction_id)


def test_saves_auction_afterwards(
        auctions_repo_mock: Mock,
        auction,
        input_dto: WithdrawingBidsInputDto,
) -> None:
    WithdrawingBids().execute(input_dto)

    auctions_repo_mock.save.assert_called_once_with(auction)


def test_calls_withdraw_bids_on_auction(
        exemplary_bids_ids: List[int],
        auction: Auction,
        input_dto: WithdrawingBidsInputDto
) -> None:
    with patch.object(Auction, 'withdraw_bids', wraps=auction.withdraw_bids) as withdraw_bids_mock:
        WithdrawingBids().execute(input_dto)

    withdraw_bids_mock.assert_called_once_with(exemplary_bids_ids)


@pytest.fixture()
def auction_with_a_winner(input_dto: WithdrawingBidsInputDto) -> Auction:
    losing_bid = Bid(id=4, bidder_id=2, amount=get_dollars('5.50'))
    winning_bid = Bid(id=2, bidder_id=1, amount=get_dollars('6.00'))
    bids = [winning_bid, losing_bid]
    ends_at = datetime.now() + timedelta(days=1)
    return Auction(
        id=2, title='does not matter', starting_price=get_dollars('5.00'), bids=bids, ends_at=ends_at
    )


def test_calls_email_gateway_once_winners_list_changes(
        auction_with_a_winner: Auction,
        email_gateway_mock: Mock,
        input_dto: WithdrawingBidsInputDto,
        auctions_repo_mock: Mock,
) -> None:
    auctions_repo_mock.get.return_value = auction_with_a_winner
    expected_bidder_id = [bid.bidder_id for bid in auction_with_a_winner.bids if bid.id not in input_dto.bids_ids].pop()

    WithdrawingBids().execute(input_dto)

    email_gateway_mock.notify_about_winning_auction.assert_called_once_with(
        auction_with_a_winner.id, expected_bidder_id
    )

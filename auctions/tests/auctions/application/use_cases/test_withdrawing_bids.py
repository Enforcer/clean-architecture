import typing
from unittest.mock import (
    Mock,
    PropertyMock,
)

import pytest

from auctions.application.use_cases import WithdrawingBidsUseCase
from auctions.application.use_cases.withdrawing_bids import WithdrawingBidsInputDto
from auctions.domain.entities import Auction


@pytest.fixture()
def exemplary_bids_ids() -> typing.List[int]:
    return [1, 2, 3]


@pytest.fixture()
def input_dto(exemplary_auction_id: int, exemplary_bids_ids: typing.List[int]) -> WithdrawingBidsInputDto:
    return WithdrawingBidsInputDto(exemplary_auction_id, exemplary_bids_ids)


def test_loads_auction_using_id(
        exemplary_auction_id: int,
        input_dto: WithdrawingBidsInputDto,
        auctions_repo_mock: Mock
) -> None:
    WithdrawingBidsUseCase().execute(input_dto)

    auctions_repo_mock.get.assert_called_once_with(exemplary_auction_id)


def test_saves_auction_afterwards(
        auctions_repo_mock: Mock,
        auction_mock: Mock,
        input_dto: WithdrawingBidsInputDto,
) -> None:
    WithdrawingBidsUseCase().execute(input_dto)

    auctions_repo_mock.save.assert_called_once_with(auction_mock)


def test_calls_withdraw_bids_on_auction(
        exemplary_bids_ids: typing.List[int],
        auction_mock: Mock,
        input_dto: WithdrawingBidsInputDto
) -> None:
    WithdrawingBidsUseCase().execute(input_dto)

    auction_mock.withdraw_bids.assert_called_once_with(exemplary_bids_ids)


def test_calls_email_gateway_once_winners_list_changes(
        exemplary_auction_id: int,
        exemplary_bids_ids: typing.List[int],
        auction_mock: Mock,
        email_gateway_mock: Mock,
        input_dto: WithdrawingBidsInputDto
) -> None:
    exemplary_new_winner_id = 1
    type(auction_mock).winners = PropertyMock(side_effect=[[], [exemplary_new_winner_id]])
    WithdrawingBidsUseCase().execute(input_dto)

    email_gateway_mock.notify_about_winning_auction.assert_called_once_with(exemplary_auction_id, exemplary_new_winner_id)

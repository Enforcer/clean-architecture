import typing
from unittest.mock import (
    Mock,
    PropertyMock,
)

import inject
import pytest

from auctions.application.interfaces import EmailGateway
from auctions.application.repositories import AuctionsRepository
from auctions.application.use_cases import WithdrawingBidsUseCase
from auctions.domain.entities import Auction


@pytest.fixture()
def exemplary_auction_id() -> int:
    return 1


@pytest.fixture()
def exemplary_bids_ids() -> int:
    return [1, 2, 3]


@pytest.fixture()
def auction_mock(exemplary_auction_id: int) -> Mock:
    mock = Mock(id=exemplary_auction_id)
    type(mock).winners = PropertyMock([])
    return mock


@pytest.fixture()
def auctions_repo_mock(auction_mock: Mock) -> Mock:
    return Mock(spec_set=AuctionsRepository, get=Mock(return_value=auction_mock))


@pytest.fixture()
def email_gateway_mock() -> Mock:
    return Mock(spec_set=EmailGateway)


@pytest.fixture(autouse=True)
def dependency_injection_config(auctions_repo_mock: Mock, email_gateway_mock: Mock) -> None:
    def configure(binder: inject.Binder) -> None:
        binder.bind(AuctionsRepository, auctions_repo_mock)
        binder.bind(EmailGateway, email_gateway_mock)

    inject.clear_and_configure(configure)


def test_loads_auction_using_id(
        exemplary_auction_id: int,
        exemplary_bids_ids: typing.List[int],
        auctions_repo_mock: Mock
) -> None:
    WithdrawingBidsUseCase().withdraw_bids(exemplary_auction_id, bids_ids=exemplary_bids_ids)

    auctions_repo_mock.get.assert_called_once_with(exemplary_auction_id)


def test_saves_auction_afterwards(
        exemplary_auction_id: int,
        exemplary_bids_ids: typing.List[int],
        auctions_repo_mock: Mock,
        auction_mock: Mock
) -> None:
    WithdrawingBidsUseCase().withdraw_bids(exemplary_auction_id, bids_ids=exemplary_bids_ids)

    auctions_repo_mock.save.assert_called_once_with(auction_mock)


def test_calls_withdraw_bids_on_auction(
        exemplary_auction_id: int,
        exemplary_bids_ids: typing.List[int],
        auction_mock: Mock
) -> None:
    WithdrawingBidsUseCase().withdraw_bids(exemplary_auction_id, bids_ids=exemplary_bids_ids)

    auction_mock.withdraw_bids.assert_called_once_with(exemplary_bids_ids)


def test_calls_email_gateway_once_winners_list_changes(
        exemplary_auction_id: int,
        exemplary_bids_ids: typing.List[int],
        auction_mock: Mock,
        email_gateway_mock: Mock
) -> None:
    exemplary_new_winner_id = 1
    type(auction_mock).winners = PropertyMock(side_effect=[[], [exemplary_new_winner_id]])
    WithdrawingBidsUseCase().withdraw_bids(exemplary_auction_id, bids_ids=exemplary_bids_ids)

    email_gateway_mock.notify_about_winning_auction.assert_called_once_with(exemplary_auction_id, exemplary_new_winner_id)

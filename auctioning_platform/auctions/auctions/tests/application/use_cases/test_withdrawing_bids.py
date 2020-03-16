from typing import List
from unittest.mock import Mock, patch

import pytest

from foundation.value_objects import Money

from auctions.application.use_cases import WithdrawingBids
from auctions.application.use_cases.withdrawing_bids import WithdrawingBidsInputDto
from auctions.domain.entities import Auction
from auctions.domain.types import AuctionId


@pytest.fixture()
def exemplary_bids_ids() -> List[int]:
    return [1, 2, 3]


@pytest.fixture()
def input_dto(auction: Auction, exemplary_bids_ids: List[int]) -> WithdrawingBidsInputDto:
    return WithdrawingBidsInputDto(auction.id, exemplary_bids_ids)


class EndingAuctionInputDto:
    def __init__(self, auction_id: AuctionId) -> None:
        self.auction_id = auction_id


class EndingAuction:
    def execute(self, dto: EndingAuctionInputDto) -> None:
        pass


class PaymentProvider:
    def begin_payment(self, amount: Money) -> None:
        pass


class PaymentProviderStub(PaymentProvider):
    def __init__(self) -> None:
        self.payments: List[Money] = []

    def begin_payment(self, amount: Money) -> None:
        self.payments.append(amount)


def test_EndingAuction_EndedAuctionWithWinner_BeginsPaymentWithAuctionCurrentPrice(
    ending_auction_uc: EndingAuction, auction: Auction, payment_provider: PaymentProviderStub
) -> None:
    ending_auction_uc.execute(EndingAuctionInputDto(auction.id))

    assert payment_provider.payments == [auction.current_price]


def test_loads_auction_using_id(
    withdrawing_bids_uc: WithdrawingBids, auction: Auction, input_dto: WithdrawingBidsInputDto, auctions_repo_mock: Mock
) -> None:
    withdrawing_bids_uc.execute(input_dto)

    auctions_repo_mock.get.assert_called_once_with(auction.id)


def test_saves_auction_afterwards(
    withdrawing_bids_uc: WithdrawingBids, auctions_repo_mock: Mock, auction: Auction, input_dto: WithdrawingBidsInputDto
) -> None:
    withdrawing_bids_uc.execute(input_dto)

    auctions_repo_mock.save.assert_called_once_with(auction)


def test_calls_withdraw_bids_on_auction(
    withdrawing_bids_uc: WithdrawingBids,
    exemplary_bids_ids: List[int],
    auction: Auction,
    input_dto: WithdrawingBidsInputDto,
) -> None:
    with patch.object(Auction, "withdraw_bids", wraps=auction.withdraw_bids) as withdraw_bids_mock:
        withdrawing_bids_uc.execute(input_dto)

    withdraw_bids_mock.assert_called_once_with(exemplary_bids_ids)

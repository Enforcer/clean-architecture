from decimal import Decimal
from unittest.mock import Mock

import pytest

from auctions.application.use_cases import PlacingBidUseCase
from auctions.application.use_cases.placing_bid import PlacingBidInputDto, PlacingBidOutputDto
from auctions.domain.entities import Bid


@pytest.fixture()
def bidder_id() -> int:
    return 1


@pytest.fixture()
def amount() -> Decimal:
    return Decimal('10.00')


@pytest.fixture()
def input_dto(exemplary_auction_id: int, bidder_id: int, amount: Decimal) -> PlacingBidInputDto:
    return PlacingBidInputDto(bidder_id, exemplary_auction_id, amount)


def test_loads_auction_using_id(
        exemplary_auction_id: int,
        auctions_repo_mock: Mock,
        input_dto: PlacingBidInputDto
) -> None:
    PlacingBidUseCase().execute(input_dto)

    auctions_repo_mock.get.assert_called_once_with(exemplary_auction_id)


def test_makes_an_expected_bid(
        input_dto: PlacingBidInputDto,
        auction_mock: Mock
) -> None:
    PlacingBidUseCase().execute(input_dto)

    auction_mock.make_a_bid.assert_called_once_with(
        Bid(id=None, amount=input_dto.amount, bidder_id=input_dto.bidder_id)
    )


def test_saves_auction(
        auctions_repo_mock: Mock,
        auction_mock: Mock,
        input_dto: PlacingBidInputDto
) -> None:
    PlacingBidUseCase().execute(input_dto)

    auctions_repo_mock.save.assert_called_once_with(auction_mock)


def test_notifies_winner(
        email_gateway_mock: Mock,
        auction_mock: Mock,
        input_dto: PlacingBidInputDto
) -> None:
    type(auction_mock).winners = [input_dto.bidder_id]

    PlacingBidUseCase().execute(input_dto)

    email_gateway_mock.notify_about_winning_auction.assert_called_once_with(input_dto.auction_id, input_dto.bidder_id)


def test_presents_output_dto(
        input_dto: PlacingBidInputDto,
        placing_bid_output_boundary_mock: Mock,
        auction_mock: Mock
) -> None:
    type(auction_mock).winners = [input_dto.bidder_id]
    auction_mock.current_price = input_dto.amount
    PlacingBidUseCase().execute(input_dto)

    desired_output_dto = PlacingBidOutputDto(is_winner=True, current_price=input_dto.amount)
    placing_bid_output_boundary_mock.present.assert_called_once_with(desired_output_dto)

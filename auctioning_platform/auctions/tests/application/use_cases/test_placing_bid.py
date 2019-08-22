from unittest.mock import Mock, patch

import pytest

from foundation.value_objects import Money
from foundation.value_objects.factories import get_dollars

from auctions.application.use_cases import PlacingBid
from auctions.application.use_cases.placing_bid import PlacingBidInputDto, PlacingBidOutputDto
from auctions.domain.entities import Auction


@pytest.fixture()
def bidder_id() -> int:
    return 1


@pytest.fixture()
def amount() -> Money:
    return get_dollars("12.00")


@pytest.fixture()
def input_dto(auction: Auction, bidder_id: int, amount: Money) -> PlacingBidInputDto:
    return PlacingBidInputDto(bidder_id, auction.id, amount)


def test_loads_auction_using_id(
    placing_bid_uc: PlacingBid, auction: Auction, auctions_repo_mock: Mock, input_dto: PlacingBidInputDto
) -> None:
    placing_bid_uc.execute(input_dto)

    auctions_repo_mock.get.assert_called_once_with(auction.id)


def test_makes_an_expected_bid(placing_bid_uc: PlacingBid, input_dto: PlacingBidInputDto, auction: Auction) -> None:
    with patch.object(Auction, "place_bid", wraps=auction.place_bid) as make_a_bid_mock:
        placing_bid_uc.execute(input_dto)

    make_a_bid_mock.assert_called_once_with(bidder_id=input_dto.bidder_id, amount=input_dto.amount)


def test_saves_auction(
    placing_bid_uc: PlacingBid, auctions_repo_mock: Mock, auction: Auction, input_dto: PlacingBidInputDto
) -> None:
    placing_bid_uc.execute(input_dto)

    auctions_repo_mock.save.assert_called_once_with(auction)


def test_presents_output_dto(
    placing_bid_uc: PlacingBid, input_dto: PlacingBidInputDto, placing_bid_output_boundary_mock: Mock, auction: Auction
) -> None:
    placing_bid_uc.execute(input_dto)

    expected_output_dto = PlacingBidOutputDto(is_winner=True, current_price=input_dto.amount)
    placing_bid_output_boundary_mock.present.assert_called_once_with(expected_output_dto)

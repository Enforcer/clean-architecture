from unittest.mock import Mock, PropertyMock

import inject
import pytest

from auctions.application.repositories import AuctionsRepository
from auctions.application.ports import EmailGateway
from auctions.application.use_cases.placing_bid import PlacingBidOutputBoundary


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


@pytest.fixture()
def placing_bid_output_boundary_mock() -> Mock:
    return Mock(spec_set=PlacingBidOutputBoundary)


@pytest.fixture(autouse=True)
def dependency_injection_config(
    auctions_repo_mock: Mock,
    email_gateway_mock: Mock,
    placing_bid_output_boundary_mock: Mock
) -> None:
    def configure(binder: inject.Binder) -> None:
        binder.bind(AuctionsRepository, auctions_repo_mock)
        binder.bind(EmailGateway, email_gateway_mock)
        binder.bind(PlacingBidOutputBoundary, placing_bid_output_boundary_mock)

    inject.clear_and_configure(configure)

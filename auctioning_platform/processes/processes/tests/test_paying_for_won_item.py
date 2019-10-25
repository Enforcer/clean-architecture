from datetime import datetime, timedelta
from typing import Generator
from unittest.mock import Mock, patch
import uuid

import freezegun
import pytest

from foundation.value_objects.factories import get_dollars

from auctions import AuctionEnded
from customer_relationship import CustomerRelationshipFacade
from payments import PaymentCaptured, PaymentsFacade

from processes.paying_for_won_item import PayingForWonItemSaga
from processes.paying_for_won_item.saga import PayingForWonItemSagaData, SagaState


@pytest.fixture()
def mocked_uuid4() -> Generator[uuid.UUID, None, None]:
    fixed_uuid = uuid.UUID("441fdf64-6d89-4664-9fce-7b026cf24f99")
    with patch.object(uuid, "uuid4", return_value=fixed_uuid):
        yield fixed_uuid


@pytest.fixture()
def payments_facade_mock() -> Mock:
    return Mock(spec_set=PaymentsFacade)


@pytest.fixture()
def customer_relationship_mock() -> Mock:
    return Mock(spec_set=CustomerRelationshipFacade)


@pytest.fixture()
def saga_data(mocked_uuid4) -> PayingForWonItemSagaData:
    return PayingForWonItemSagaData(mocked_uuid4)


@pytest.fixture()
def saga(payments_facade_mock: Mock, customer_relationship_mock: Mock) -> PayingForWonItemSaga:
    return PayingForWonItemSaga(payments_facade_mock, customer_relationship_mock)


@pytest.mark.freeze_time("2019-03-25 15:38:00")
def test_should_start_new_payment_upon_auction_ended(
    saga: PayingForWonItemSaga,
    payments_facade_mock: Mock,
    customer_relationship_mock: Mock,
    mocked_uuid4: uuid.UUID,
    saga_data: PayingForWonItemSagaData,
) -> None:
    event = AuctionEnded(auction_id=1, winner_id=2, winning_bid=get_dollars("99.99"), auction_title="irrelevant")
    saga.handle(event, saga_data)

    payments_facade_mock.start_new_payment.assert_called_once_with(
        mocked_uuid4, event.winner_id, event.winning_bid, event.auction_title
    )
    customer_relationship_mock.send_email_about_winning.assert_called_once_with(
        event.winner_id, event.winning_bid, event.auction_title
    )
    assert saga_data.state == SagaState.PAYMENT_STARTED
    assert saga_data.winning_bid == event.winning_bid
    assert saga_data.auction_title == event.auction_title
    assert saga_data.timeout_at == datetime.now() + timedelta(days=3)
    assert saga_data.winner_id == event.winner_id
    assert saga_data.auction_id == event.auction_id


@pytest.fixture()
def saga_data_waiting_for_payment(mocked_uuid4: uuid.UUID, saga: PayingForWonItemSaga) -> PayingForWonItemSagaData:
    return PayingForWonItemSagaData(
        mocked_uuid4, SagaState.PAYMENT_STARTED, datetime.now() + timedelta(days=3), get_dollars("15.99"), "Irrelevant"
    )


def test_should_send_success_email_after_payment(
    mocked_uuid4: uuid.UUID,
    saga: PayingForWonItemSaga,
    customer_relationship_mock: Mock,
    saga_data_waiting_for_payment: PayingForWonItemSagaData,
) -> None:
    event = PaymentCaptured(mocked_uuid4, 2)
    saga.handle(event, saga_data_waiting_for_payment)

    customer_relationship_mock.send_email_after_successful_payment.assert_called_once_with(
        event.customer_id, saga_data_waiting_for_payment.winning_bid, saga_data_waiting_for_payment.auction_title
    )
    assert saga_data_waiting_for_payment.state == SagaState.FINISHED
    assert saga_data_waiting_for_payment.timeout_at is None


def test_should_timeout(
    mocked_uuid4: uuid.UUID,
    saga: PayingForWonItemSaga,
    customer_relationship_mock: Mock,
    saga_data_waiting_for_payment: PayingForWonItemSagaData,
) -> None:
    with freezegun.freeze_time(datetime.now() + timedelta(days=4)):
        saga.timeout(saga_data_waiting_for_payment)

    assert saga_data_waiting_for_payment.state == SagaState.TIMED_OUT

from unittest.mock import patch
import uuid

from _pytest.fixtures import SubRequest
import pytest
from sqlalchemy.engine import Connection, Engine, RowProxy

from foundation.value_objects.factories import get_dollars

from db_infrastructure import Base

from payments import PaymentsConfig, PaymentsFacade
from payments.api import ApiConsumer
from payments.api.exceptions import PaymentFailedError
from payments.dao import PaymentDto, PaymentStatus
from payments.models import payments


@pytest.fixture(scope="session")
def sqlalchemy_connect_url() -> str:
    return "sqlite:///:memory:"


@pytest.fixture(scope="session", autouse=True)
def setup_teardown_tables(engine: Engine) -> None:
    Base.metadata.create_all(engine)


@pytest.fixture()
def facade(connection: Connection) -> PaymentsFacade:
    return PaymentsFacade(PaymentsConfig("", ""), lambda: connection)


@pytest.fixture()
def inserted_payment(request: SubRequest, connection: Connection) -> dict:
    data = {
        "uuid": str(uuid.uuid4()),
        "customer_id": 1,
        "amount": 100,
        "currency": "USD",
        "status": getattr(request, "param", None) or PaymentStatus.NEW.value,
        "description": "irrelevant",
    }
    connection.execute(payments.insert(data))
    return data


def get_payment(connection: Connection, payment_uuid: str) -> RowProxy:
    row = connection.execute(payments.select(payments.c.uuid == payment_uuid)).first()
    return row


@pytest.mark.usefixtures("transaction")
def test_adding_new_payment_is_reflected_on_pending_payments_list(
    facade: PaymentsFacade, connection: Connection
) -> None:
    customer_id = 1
    assert facade.get_pending_payments(customer_id) == []

    payment_uuid = uuid.uuid4()
    amount = get_dollars("15.00")
    description = "Example"
    facade.start_new_payment(payment_uuid, customer_id, amount, description)

    row, = connection.execute(payments.select()).fetchall()
    assert dict(row) == {
        "uuid": str(payment_uuid),
        "customer_id": customer_id,
        "amount": int(amount.amount * 100),
        "currency": amount.currency.iso_code,
        "status": PaymentStatus.NEW.value,
        "description": description,
        "charge_id": None,
    }

    pending_payments = facade.get_pending_payments(customer_id)

    assert pending_payments == [PaymentDto(payment_uuid, amount, description, PaymentStatus.NEW.value)]


@pytest.mark.parametrize(
    "inserted_payment",
    [status.value for status in PaymentStatus if status != PaymentStatus.NEW],
    indirect=["inserted_payment"],
)
@pytest.mark.usefixtures("transaction")
def test_pending_payments_returns_only_new_payments(
    facade: PaymentsFacade, inserted_payment: dict, connection: Connection
) -> None:
    assert facade.get_pending_payments(inserted_payment["customer_id"]) == []


@pytest.mark.usefixtures("transaction")
def test_successful_charge_updates_status(
    facade: PaymentsFacade, inserted_payment: dict, connection: Connection
) -> None:
    charge_id = "SOME_CHARGE_ID"
    with patch.object(ApiConsumer, "charge", return_value=charge_id) as charge_mock:
        facade.pay(uuid.UUID(inserted_payment["uuid"]), inserted_payment["customer_id"], "token")

    charge_mock.assert_called_once_with(
        get_dollars(inserted_payment["amount"] / 100), "token", inserted_payment["uuid"]
    )
    payment_row = get_payment(connection, inserted_payment["uuid"])
    assert payment_row.status == PaymentStatus.CHARGED.value
    assert payment_row.charge_id == charge_id


@pytest.mark.usefixtures("transaction")
def test_unsuccessful_charge_updates_status(
    facade: PaymentsFacade, inserted_payment: dict, connection: Connection
) -> None:
    with patch.object(ApiConsumer, "charge", side_effect=PaymentFailedError) as charge_mock:
        facade.pay(uuid.UUID(inserted_payment["uuid"]), inserted_payment["customer_id"], "token")

    charge_mock.assert_called_once_with(
        get_dollars(inserted_payment["amount"] / 100), "token", inserted_payment["uuid"]
    )
    assert get_payment(connection, inserted_payment["uuid"]).status == PaymentStatus.FAILED.value

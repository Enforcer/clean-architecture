from datetime import datetime
import json
from uuid import UUID, uuid4

import pytest
from sqlalchemy.engine import Connection, Engine

from foundation.value_objects.factories import get_dollars

from db_infrastructure import Base

from processes.paying_for_won_item import PayingForWonItemSagaData
from processes.paying_for_won_item.saga import SagaState
from processes.repository import SagaDataRepo, saga_data_table

EXAMPLE_DATETIME = datetime(2019, 5, 24, 15, 20, 0, 12)


@pytest.fixture(scope="session")
def sqlalchemy_connect_url() -> str:
    return "sqlite:///:memory:"


@pytest.fixture(scope="session", autouse=True)
def setup_teardown_tables(engine: Engine) -> None:
    Base.metadata.create_all(engine)


@pytest.fixture()
def repo(connection: Connection) -> SagaDataRepo:
    return SagaDataRepo(connection)


@pytest.mark.parametrize(
    "data, json_repr",
    [
        (
            PayingForWonItemSagaData(UUID("331831f1-3d7c-48c2-9433-955c1cf8deb6")),
            {
                "saga_uuid": "331831f1-3d7c-48c2-9433-955c1cf8deb6",
                "state": None,
                "timeout_at": None,
                "winning_bid": None,
                "auction_title": None,
                "auction_id": None,
                "winner_id": None,
            },
        ),
        (
            PayingForWonItemSagaData(
                UUID("d1526bb4-cee4-4b63-9029-802abc0f7593"),
                SagaState.PAYMENT_STARTED,
                EXAMPLE_DATETIME,
                get_dollars("15.99"),
                "Irrelevant",
                1,
                2,
            ),
            {
                "saga_uuid": "d1526bb4-cee4-4b63-9029-802abc0f7593",
                "state": SagaState.PAYMENT_STARTED.value,
                "timeout_at": EXAMPLE_DATETIME.isoformat(),
                "winning_bid": {"amount": "15.99", "currency": "USD"},
                "auction_title": "Irrelevant",
                "auction_id": 1,
                "winner_id": 2,
            },
        ),
    ],
)
def test_saving_and_reading(
    repo: SagaDataRepo, connection: Connection, data: PayingForWonItemSagaData, json_repr: dict
) -> None:
    saga_uuid = uuid4()

    connection.execute(saga_data_table.insert(values={"uuid": saga_uuid, "json": json.dumps(json_repr)}))

    assert repo.get(saga_uuid, type(data)) == data

    connection.execute(saga_data_table.delete().where(saga_data_table.c.uuid == saga_uuid))

    repo.save(saga_uuid, data)

    row = connection.execute(saga_data_table.select(saga_data_table.c.uuid == saga_uuid)).first()
    assert json.loads(row.json) == json_repr

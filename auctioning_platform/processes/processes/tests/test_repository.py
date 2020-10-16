from datetime import datetime
import json
from uuid import UUID, uuid4

import pytest
from sqlalchemy.engine import Connection, Engine

from foundation.value_objects.factories import get_dollars

from db_infrastructure import Base
from processes.paying_for_won_item import PayingForWonItemData
from processes.paying_for_won_item.saga import State
from processes.repository import ProcessManagerDataRepo, process_manager_data_table

EXAMPLE_DATETIME = datetime(2019, 5, 24, 15, 20, 0, 12)


@pytest.fixture(scope="session")
def sqlalchemy_connect_url() -> str:
    return "sqlite:///:memory:"


@pytest.fixture(scope="session", autouse=True)
def setup_teardown_tables(engine: Engine) -> None:
    Base.metadata.create_all(engine)


@pytest.fixture()
def repo(connection: Connection) -> ProcessManagerDataRepo:
    return ProcessManagerDataRepo(connection)


@pytest.mark.parametrize(
    "data, json_repr",
    [
        (
            PayingForWonItemData(UUID("331831f1-3d7c-48c2-9433-955c1cf8deb6")),
            {
                "process_uuid": "331831f1-3d7c-48c2-9433-955c1cf8deb6",
                "state": None,
                "timeout_at": None,
                "winning_bid": None,
                "auction_title": None,
                "auction_id": None,
                "winner_id": None,
            },
        ),
        (
            PayingForWonItemData(
                UUID("d1526bb4-cee4-4b63-9029-802abc0f7593"),
                State.PAYMENT_STARTED,
                EXAMPLE_DATETIME,
                get_dollars("15.99"),
                "Irrelevant",
                1,
                2,
            ),
            {
                "process_uuid": "d1526bb4-cee4-4b63-9029-802abc0f7593",
                "state": State.PAYMENT_STARTED.value,
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
    repo: ProcessManagerDataRepo, connection: Connection, data: PayingForWonItemData, json_repr: dict
) -> None:
    process_uuid = uuid4()

    connection.execute(process_manager_data_table.insert(values={"uuid": process_uuid, "json": json.dumps(json_repr)}))

    assert repo.get(process_uuid, type(data)) == data

    connection.execute(process_manager_data_table.delete().where(process_manager_data_table.c.uuid == process_uuid))

    repo.save(process_uuid, data)

    row = connection.execute(
        process_manager_data_table.select(process_manager_data_table.c.uuid == process_uuid)
    ).first()
    assert json.loads(row.json) == json_repr

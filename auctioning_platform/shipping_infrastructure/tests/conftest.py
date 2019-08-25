import uuid

import pytest
from sqlalchemy.engine import Connection, RowProxy
from sqlalchemy.engine import Engine

from db_infrastructure import Base

from shipping.domain.types import ConsigneeId
from shipping.domain.value_objects import PackageStatus
from shipping_infrastructure.models import packages


@pytest.fixture(scope="session")
def sqlalchemy_connect_url() -> str:
    return "sqlite:///:memory:"


@pytest.fixture(scope="session", autouse=True)
def setup_teardown_tables(engine: Engine) -> None:
    Base.metadata.create_all(engine)


@pytest.fixture()
def consignee_id() -> ConsigneeId:
    return 1


@pytest.fixture()
def raw_address_details() -> dict:
    return {
        "street": "Nancy Grove",
        "house_number": "517",
        "city": "Trevinoport",
        "state": "Utah",
        "zip_code": "30954",
        "country": "Bouvet Island (Bouvetoya)",
    }


@pytest.fixture()
def raw_package(consignee_id: ConsigneeId, raw_address_details: dict) -> dict:
    return {
        "uuid": uuid.UUID("742febe3-da50-4b43-957f-62909d2bb5d7"),
        "item_identifier": "iPhone X 64 GB Space Gray",
        "consignee_id": consignee_id,
        "status": PackageStatus.CREATED,
        **raw_address_details
    }


@pytest.fixture()
def package_model(connection: Connection, raw_package: dict) -> RowProxy:
    connection.execute(packages.insert().values(raw_package))
    return connection.execute(packages.select(whereclause=packages.c.uuid == raw_package["uuid"])).first()

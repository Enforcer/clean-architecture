import uuid

import pytest

from sqlalchemy.engine import Connection, RowProxy

from shipping.domain.types import ConsigneeId
from shipping.domain.value_objects import PackageStatus

from shipping_infrastructure.models import packages


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
def raw_created_package(consignee_id: ConsigneeId, raw_address_details: dict) -> dict:
    return {
        "uuid": uuid.UUID("742febe3-da50-4b43-957f-62909d2bb5d7"),
        "item_identifier": "iPhone X 64 GB Space Gray",
        "consignee_id": consignee_id,
        "status": PackageStatus.CREATED,
        **raw_address_details
    }


@pytest.fixture()
def raw_shipped_package(consignee_id: ConsigneeId, raw_address_details: dict) -> dict:
    return {
        "uuid": uuid.UUID("d82ca97e-d7a1-4613-9c2c-90307790a32c"),
        "item_identifier": "Sony PlayStation 4 Pro 1TB Black",
        "consignee_id": consignee_id,
        "status": PackageStatus.SHIPPED,
        **raw_address_details
    }


@pytest.fixture()
def created_package_model(connection: Connection, raw_created_package: dict) -> RowProxy:
    connection.execute(packages.insert().values(raw_created_package))
    return connection.execute(packages.select(whereclause=packages.c.uuid == raw_created_package["uuid"])).first()


@pytest.fixture()
def shipped_package_model(connection: Connection, raw_shipped_package: dict) -> RowProxy:
    connection.execute(packages.insert().values(raw_shipped_package))
    return connection.execute(packages.select(whereclause=packages.c.uuid == raw_shipped_package["uuid"])).first()

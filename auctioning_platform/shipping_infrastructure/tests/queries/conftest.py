import uuid

import pytest
from sqlalchemy.engine import Connection, RowProxy

from shipping.domain.types import ConsigneeId
from shipping.domain.value_objects import PackageStatus

from shipping_infrastructure.models import packages


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
def shipped_package_model(connection: Connection, raw_shipped_package: dict) -> RowProxy:
    connection.execute(packages.insert().values(raw_shipped_package))
    return connection.execute(packages.select(whereclause=packages.c.uuid == raw_shipped_package["uuid"])).first()

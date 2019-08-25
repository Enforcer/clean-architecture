import copy
import uuid
from typing import Generator
from unittest.mock import patch

import pytest

from shipping.domain.entities import Address, Package
from shipping.domain.types import ConsigneeId
from shipping.domain.value_objects import PackageStatus


@pytest.fixture()
def mocked_uuid4() -> Generator[uuid.UUID, None, None]:
    fixed_uuid = uuid.UUID("742febe3-da50-4b43-957f-62909d2bb5d7")
    with patch.object(uuid, "uuid4", return_value=fixed_uuid):
        yield fixed_uuid


@pytest.fixture()
def item_identifier() -> str:
    return "iPhone X 64 GB Space Gray"


@pytest.fixture()
def consignee_id() -> ConsigneeId:
    return 1


@pytest.fixture()
def address() -> Address:
    return Address(
        uuid=uuid.UUID("5015b850-4773-4bdb-8aeb-ce452cb4676a"),
        street="Nancy Grove",
        house_number="517",
        city="Trevinoport",
        state="Utah",
        zip_code="30954",
        country="Bouvet Island (Bouvetoya)",
    )


@pytest.fixture()
def package(item_identifier: str, consignee_id: ConsigneeId, address: Address, mocked_uuid4: uuid.UUID) -> Package:
    return Package(
        uuid=mocked_uuid4,
        item_identifier=item_identifier,
        consignee_id=consignee_id,
        street=address.street,
        house_number=address.house_number,
        city=address.city,
        state=address.state,
        zip_code=address.zip_code,
        country=address.country,
        status=PackageStatus.CREATED,
    )


@pytest.fixture()
def shipped_package(package: Package) -> Package:
    package_copy = copy.deepcopy(package)
    package_copy.ship()
    return package_copy

import uuid
from typing import Generator
from unittest.mock import Mock, patch

import pytest

from shipping.application.repositories import AddressRepository, PackageRepository
from shipping.application.use_cases import RegisteringPackage, RegisteringPackageInputDto
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
def address_repo_mock(address: Address) -> Mock:
    return Mock(spec_set=AddressRepository, get=Mock(return_value=address))


@pytest.fixture()
def package_repo_mock() -> Mock:
    return Mock(spec_set=PackageRepository)


@pytest.fixture()
def registering_package_input_dto(item_identifier: str, consignee_id: ConsigneeId) -> RegisteringPackageInputDto:
    return RegisteringPackageInputDto(item_identifier, consignee_id)


@pytest.fixture()
def registering_package_uc(address_repo_mock: Mock, package_repo_mock: Mock) -> RegisteringPackage:
    return RegisteringPackage(address_repo_mock, package_repo_mock)

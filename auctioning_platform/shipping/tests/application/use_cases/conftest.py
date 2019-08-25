import uuid
from unittest.mock import Mock

import pytest

from shipping.application.repositories import AddressRepository, PackageRepository
from shipping.application.use_cases import (
    RegisteringPackage,
    RegisteringPackageInputDto,
    ShippingPackage,
    ShippingPackageInputDto,
)
from shipping.domain.entities import Address, Package
from shipping.domain.types import ConsigneeId


@pytest.fixture()
def address_repo_mock(address: Address) -> Mock:
    return Mock(spec_set=AddressRepository, get=Mock(return_value=address))


@pytest.fixture()
def package_repo_mock(package: Package) -> Mock:
    return Mock(spec_set=PackageRepository, get=Mock(return_value=package))


@pytest.fixture()
def registering_package_input_dto(item_identifier: str, consignee_id: ConsigneeId) -> RegisteringPackageInputDto:
    return RegisteringPackageInputDto(item_identifier, consignee_id)


@pytest.fixture()
def registering_package_uc(address_repo_mock: Mock, package_repo_mock: Mock) -> RegisteringPackage:
    return RegisteringPackage(address_repo_mock, package_repo_mock)


@pytest.fixture()
def shipping_package_input_dto(mocked_uuid4: uuid.UUID) -> ShippingPackageInputDto:
    return ShippingPackageInputDto(mocked_uuid4)


@pytest.fixture()
def shipping_package_uc(package_repo_mock: Mock) -> ShippingPackage:
    return ShippingPackage(package_repo_mock)

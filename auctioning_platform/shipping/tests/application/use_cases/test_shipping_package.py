from unittest.mock import Mock

from shipping.application.use_cases import ShippingPackage
from shipping.application.use_cases.shipping_package import ShippingPackageInputDto
from shipping.domain.entities import Package


def test_loads_package_by_uuid(
    shipping_package_uc: ShippingPackage, shipping_package_input_dto: ShippingPackageInputDto, package_repo_mock: Mock
) -> None:
    shipping_package_uc.execute(shipping_package_input_dto)

    package_repo_mock.get.assert_called_once_with(shipping_package_input_dto.package_uuid)


def test_saves_updated_package(
    shipping_package_uc: ShippingPackage,
    shipping_package_input_dto: ShippingPackageInputDto,
    package_repo_mock: Mock,
    shipped_package: Package,
) -> None:
    shipping_package_uc.execute(shipping_package_input_dto)

    package_repo_mock.save.assert_called_once_with(shipped_package)

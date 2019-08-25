from unittest.mock import Mock

from shipping.application.use_cases import RegisteringPackage, RegisteringPackageInputDto
from shipping.domain.entities import Package


def test_uses_repository_to_get_consignee_address(
    registering_package_uc: RegisteringPackage,
    registering_package_input_dto: RegisteringPackageInputDto,
    address_repo_mock: Mock,
) -> None:
    registering_package_uc.execute(registering_package_input_dto)

    address_repo_mock.get.assert_called_once_with(registering_package_input_dto.consignee_id)


def test_saves_new_package(
    registering_package_uc: RegisteringPackage,
    registering_package_input_dto: RegisteringPackageInputDto,
    package_repo_mock: Mock,
    package: Package,
) -> None:
    registering_package_uc.execute(registering_package_input_dto)

    package_repo_mock.save.assert_called_once_with(package)

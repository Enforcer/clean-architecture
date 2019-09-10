from dataclasses import dataclass
from uuid import UUID

# from shipping.application.repositories import PackageRepository


@dataclass
class ShippingPackageInputDto:
    package_uuid: UUID


class ShippingPackage:
    pass
    # def __init__(self, package_repo: PackageRepository) -> None:
    #     self.package_repo = package_repo
    #
    # def execute(self, input_dto: ShippingPackageInputDto) -> None:
    #     package = self.package_repo.get(input_dto.package_uuid)
    #     # TODO: continue work on that...

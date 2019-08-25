import uuid
from dataclasses import dataclass

from shipping.application.repositories import AddressRepository, PackageRepository
from shipping.domain.entities import Package
from shipping.domain.types import ConsigneeId


@dataclass
class RegisteringPackageInputDto:
    item_identifier: str
    consignee_id: ConsigneeId


class RegisteringPackage:
    def __init__(self, address_repo: AddressRepository, package_repo: PackageRepository) -> None:
        self.address_repo = address_repo
        self.package_repo = package_repo

    def execute(self, input_dto: RegisteringPackageInputDto) -> None:
        consignee_address = self.address_repo.get(input_dto.consignee_id)
        package = Package(
            uuid=uuid.uuid4(),
            item_identifier=input_dto.item_identifier,
            consignee_id=input_dto.consignee_id,
            street=consignee_address.street,
            house_number=consignee_address.house_number,
            city=consignee_address.city,
            state=consignee_address.state,
            zip_code=consignee_address.zip_code,
            country=consignee_address.country,
        )
        self.package_repo.save(package)

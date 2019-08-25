import injector

from shipping.application.queries import GetNextPackage, PackageDto
from shipping.application.repositories import AddressRepository, PackageRepository
from shipping.application.use_cases import (
    RegisteringPackage,
    RegisteringPackageInputDto,
    ShippingPackage,
    ShippingPackageInputDto,
)

__all__ = [
    # module
    "Shipping",
    # events
    # repositories
    "AddressRepository",
    "PackageRepository",
    # use cases
    "RegisteringPackage",
    "RegisteringPackageInputDto",
    "ShippingPackage",
    "ShippingPackageInputDto",
    # queries
    "GetNextPackage",
    "PackageDto",
]


class Shipping(injector.Module):
    @injector.provider
    def registering_package_uc(
        self, address_repo: AddressRepository, package_repo: PackageRepository
    ) -> RegisteringPackage:
        return RegisteringPackage(address_repo, package_repo)

    @injector.provider
    def shipping_package_uc(self, package_repo: PackageRepository) -> ShippingPackage:
        return ShippingPackage(package_repo)

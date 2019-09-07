import injector

from shipping import AddressRepository

from shipping_infrastructure.models import packages
from shipping_infrastructure.repositories import FakeAddressRepository

__all__ = [
    # module
    "ShippingInfrastructure",
    # models
    "packages",
]


class ShippingInfrastructure(injector.Module):
    @injector.provider
    def address_repo(self) -> AddressRepository:
        return FakeAddressRepository()

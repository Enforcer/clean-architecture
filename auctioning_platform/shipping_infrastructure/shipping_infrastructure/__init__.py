import injector
# from sqlalchemy.engine import Connection

from shipping import AddressRepository  # GetNextPackage

from shipping_infrastructure.models import packages
# from shipping_infrastructure.queries import SqlGetNextPackage
from shipping_infrastructure.repositories import FakeAddressRepository

__all__ = [
    # module
    "ShippingInfrastructure",
    # models
    "packages",
]


class ShippingInfrastructure(injector.Module):
    # @injector.provider
    # def get_next_package_query(self, conn: Connection) -> GetNextPackage:
    #     return SqlGetNextPackage(conn)

    @injector.provider
    def address_repo(self) -> AddressRepository:
        return FakeAddressRepository()

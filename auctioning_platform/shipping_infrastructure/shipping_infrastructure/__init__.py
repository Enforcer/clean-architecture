import injector
from sqlalchemy.engine import Connection

from shipping import AddressRepository, GetNextPackage, PackageRepository

from shipping_infrastructure.models import packages
from shipping_infrastructure.queries import SqlGetNextPackage
from shipping_infrastructure.repositories import FakeAddressRepository, SqlAlchemyPackageRepository

__all__ = [
    # module
    "ShippingInfrastructure",
    # models
    "packages",
]


class ShippingInfrastructure(injector.Module):
    @injector.provider
    def get_next_package_query(self, conn: Connection) -> GetNextPackage:
        return SqlGetNextPackage(conn)

    @injector.provider
    def address_repo(self) -> AddressRepository:
        return FakeAddressRepository()

    @injector.provider
    def package_repo(self, conn: Connection) -> PackageRepository:
        return SqlAlchemyPackageRepository(conn)

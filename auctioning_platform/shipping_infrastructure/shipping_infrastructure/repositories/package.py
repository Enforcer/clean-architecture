import uuid

from sqlalchemy.engine import Connection

from shipping import PackageRepository
from shipping.domain.entities import Package

from shipping_infrastructure.models import packages


class SqlAlchemyPackageRepository(PackageRepository):
    def __init__(self, connection: Connection) -> None:
        self._conn = connection

    def get(self, package_uuid: uuid.UUID) -> Package:
        pass

    def save(self, package: Package) -> None:
        raw_package = {
            "uuid": package.uuid,
            "item_identifier": package.item_identifier,
            "consignee_id": package.consignee_id,
            "street": package.street,
            "house_number": package.house_number,
            "city": package.city,
            "state": package.state,
            "zip_code": package.zip_code,
            "country": package.country,
            "status": package.status,
        }
        result = self._conn.execute(packages.insert(values=raw_package))
        assert result.rowcount == 1

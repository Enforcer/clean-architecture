import uuid

from sqlalchemy.engine import Connection, RowProxy

from shipping import PackageRepository
from shipping.domain.entities import Package

from shipping_infrastructure.exceptions import PackageNotFound
from shipping_infrastructure.models import packages


class SqlAlchemyPackageRepository(PackageRepository):
    def __init__(self, connection: Connection) -> None:
        self._conn = connection

    def get(self, package_uuid: uuid.UUID) -> Package:
        row = self._conn.execute(packages.select().where(packages.c.uuid == package_uuid)).first()
        if not row:
            raise PackageNotFound
        return self._row_to_entity(row)

    def _row_to_entity(self, package_proxy: RowProxy) -> Package:
        return Package(
            uuid=package_proxy.uuid,
            item_identifier=package_proxy.item_identifier,
            consignee_id=package_proxy.consignee_id,
            street=package_proxy.street,
            house_number=package_proxy.house_number,
            city=package_proxy.city,
            state=package_proxy.state,
            zip_code=package_proxy.zip_code,
            country=package_proxy.country,
            status=package_proxy.status
        )

    def save(self, package: Package) -> None:
        raw_package = self._entity_to_raw(package)
        row = self._conn.execute(packages.select().where(packages.c.uuid == package.uuid)).first()
        if not row:
            result = self._conn.execute(packages.insert(values=raw_package))
        else:
            result = self._conn.execute(packages.update(values=raw_package))
        assert result.rowcount == 1

    def _entity_to_raw(self, package: Package) -> dict:
        return {
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

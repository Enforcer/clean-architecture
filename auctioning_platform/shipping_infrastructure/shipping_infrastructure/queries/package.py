from typing import Optional

from sqlalchemy.engine import RowProxy

from shipping import GetNextPackage, PackageDto
from shipping.domain.value_objects import PackageStatus

from shipping_infrastructure.models import packages
from shipping_infrastructure.queries.base import SqlQuery


class SqlGetNextPackage(GetNextPackage, SqlQuery):
    def query(self) -> Optional[PackageDto]:
        row = self._conn.execute(packages.select().where(packages.c.status == PackageStatus.CREATED)).first()
        return _row_to_dto(row) if row is not None else None


def _row_to_dto(package_proxy: RowProxy) -> PackageDto:
    return PackageDto(
        uuid=package_proxy.uuid,
        item_identifier=package_proxy.item_identifier,
        street=package_proxy.street,
        house_number=package_proxy.house_number,
        city=package_proxy.city,
        state=package_proxy.state,
        zip_code=package_proxy.zip_code,
        country=package_proxy.country,
    )

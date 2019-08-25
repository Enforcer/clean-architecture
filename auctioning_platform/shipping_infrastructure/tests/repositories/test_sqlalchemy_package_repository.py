import pytest
from sqlalchemy import func, select
from sqlalchemy.engine import Connection

from shipping.domain.entities import Package

from shipping_infrastructure.models import packages
from shipping_infrastructure.repositories import SqlAlchemyPackageRepository


@pytest.mark.usefixtures("transaction")
def test_saves_new_package(connection: Connection, package: Package) -> None:
    SqlAlchemyPackageRepository(connection).save(package)

    assert connection.execute(select([func.count()]).select_from(packages)).scalar() == 1

import pytest
from sqlalchemy import func, select
from sqlalchemy.engine import Connection

from shipping.domain.entities import Package
from shipping.domain.value_objects import PackageStatus
from shipping_infrastructure.exceptions import PackageNotFound

from shipping_infrastructure.models import packages
from shipping_infrastructure.repositories import SqlAlchemyPackageRepository


@pytest.mark.usefixtures("transaction", "package_model")
def test_gets_package(connection: Connection, package: Package) -> None:
    actual_package = SqlAlchemyPackageRepository(connection).get(package.uuid)

    assert actual_package == package


@pytest.mark.usefixtures("transaction")
def test_raises_exception_when_package_has_not_been_found(connection: Connection, package: Package) -> None:
    with pytest.raises(PackageNotFound):
        SqlAlchemyPackageRepository(connection).get(package.uuid)


@pytest.mark.usefixtures("transaction")
def test_saves_new_package(connection: Connection, package: Package) -> None:
    SqlAlchemyPackageRepository(connection).save(package)

    assert connection.execute(select([func.count()]).select_from(packages)).scalar() == 1


@pytest.mark.usefixtures("transaction", "package_model")
def test_updates_package(connection: Connection, shipped_package: Package) -> None:
    SqlAlchemyPackageRepository(connection).save(shipped_package)

    assert connection.execute(select([func.count()]).select_from(packages)).scalar() == 1
    updated_package = connection.execute(packages.select().where(packages.c.uuid == str(shipped_package.uuid))).first()
    assert updated_package.status == PackageStatus.SHIPPED

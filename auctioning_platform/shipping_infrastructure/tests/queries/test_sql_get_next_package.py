import pytest
from sqlalchemy.engine import Connection, RowProxy

from shipping_infrastructure.queries import SqlGetNextPackage


@pytest.mark.usefixtures("transaction", "shipped_package_model")
def test_gets_next_package(connection: Connection, created_package_model: RowProxy) -> None:
    package = SqlGetNextPackage(connection).query()

    assert package.uuid == created_package_model.uuid
    assert package.item_identifier == created_package_model.item_identifier


@pytest.mark.usefixtures("transaction", "shipped_package_model")
def test_gets_none_when_there_is_no_next_package(connection: Connection) -> None:
    package = SqlGetNextPackage(connection).query()

    assert package is None

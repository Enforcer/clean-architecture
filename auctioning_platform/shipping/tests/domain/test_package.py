import pytest

from shipping.domain.entities import Package
from shipping.domain.exceptions import PackageAlreadyShipped
from shipping.domain.value_objects import PackageStatus


def test_ship_package(package: Package) -> None:
    package.ship()

    assert package.status == PackageStatus.SHIPPED


def test_should_not_let_to_ship_already_shipped_package(shipped_package: Package) -> None:
    with pytest.raises(PackageAlreadyShipped):
        shipped_package.ship()

import copy

import pytest

from shipping.domain.entities import Package


@pytest.fixture()
def package(raw_package: dict) -> Package:
    return Package(
        uuid=raw_package["uuid"],
        item_identifier=raw_package["item_identifier"],
        consignee_id=raw_package["consignee_id"],
        street=raw_package["street"],
        house_number=raw_package["house_number"],
        city=raw_package["city"],
        state=raw_package["state"],
        zip_code=raw_package["zip_code"],
        country=raw_package["country"],
        status=raw_package["status"],
    )


@pytest.fixture()
def shipped_package(package: Package) -> Package:
    package_copy = copy.deepcopy(package)
    package_copy.ship()
    return package_copy

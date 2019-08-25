import uuid

import pytest
from sqlalchemy.engine import Engine

from db_infrastructure import Base

from shipping.domain.entities import Package


@pytest.fixture(scope="session")
def sqlalchemy_connect_url() -> str:
    return "sqlite:///:memory:"


@pytest.fixture(scope="session", autouse=True)
def setup_teardown_tables(engine: Engine) -> None:
    Base.metadata.create_all(engine)


@pytest.fixture()
def package() -> Package:
    return Package(
        uuid=uuid.UUID("742febe3-da50-4b43-957f-62909d2bb5d7"),
        item_identifier="iPhone X 64 GB Space Gray",
        consignee_id=1,
        street="Nancy Grove",
        house_number="517",
        city="Trevinoport",
        state="Utah",
        zip_code="30954",
        country="Bouvet Island (Bouvetoya)",
    )

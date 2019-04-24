from datetime import datetime, timedelta
from unittest.mock import Mock

from pybuses import EventBus
import pytest
import pytz


@pytest.fixture()
def ends_at() -> datetime:
    return datetime.now(tz=pytz.UTC) + timedelta(days=3)


@pytest.fixture()
def past_date() -> datetime:
    return datetime.now(tz=pytz.UTC) - timedelta(days=15)


@pytest.fixture()
def event_bus_mock() -> Mock:
    return Mock(spec_set=EventBus)

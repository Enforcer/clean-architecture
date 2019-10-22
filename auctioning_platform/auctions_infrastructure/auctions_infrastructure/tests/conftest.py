from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest
import pytz

from foundation.events import EventBus


@pytest.fixture()
def ends_at() -> datetime:
    return datetime.now(tz=pytz.UTC) + timedelta(days=3)


@pytest.fixture()
def past_date() -> datetime:
    return datetime.now(tz=pytz.UTC) - timedelta(days=15)


@pytest.fixture()
def event_bus_mock() -> Mock:
    return Mock(spec_set=EventBus)

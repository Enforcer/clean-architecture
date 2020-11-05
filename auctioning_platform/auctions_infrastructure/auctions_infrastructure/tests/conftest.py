from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest
import pytz

from foundation.events import EventBus


@pytest.fixture()
def ends_at() -> datetime:
    """
    Returns a datetime. timedelta. datetime. datetime.

    Args:
    """
    return datetime.now(tz=pytz.UTC) + timedelta(days=3)


@pytest.fixture()
def past_date() -> datetime:
    """
    Returns a datetime.

    Args:
    """
    return datetime.now(tz=pytz.UTC) - timedelta(days=15)


@pytest.fixture()
def event_bus_mock() -> Mock:
    """
    Return a mock socket object for the given socket.

    Args:
    """
    return Mock(spec_set=EventBus)

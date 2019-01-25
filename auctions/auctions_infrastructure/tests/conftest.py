from datetime import (
    datetime,
    timedelta,
)

import pytest
import pytz


@pytest.fixture()
def ends_at() -> datetime:
    return datetime.now(tz=pytz.UTC) + timedelta(days=3)


@pytest.fixture()
def past_date() -> datetime:
    return datetime.now(tz=pytz.UTC) - timedelta(days=15)

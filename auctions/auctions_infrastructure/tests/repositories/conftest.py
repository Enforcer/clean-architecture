from datetime import (
    datetime,
    timedelta,
)

import pytest
from django.utils import timezone


@pytest.fixture()
def ends_at() -> datetime:
    return timezone.now() + timedelta(days=3)

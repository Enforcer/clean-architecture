from datetime import datetime

from _pytest.fixtures import SubRequest
import pytest
import requests

from foundation.value_objects.factories import get_dollars

from payments.api import ApiConsumer
from payments.api.requests import Request


@pytest.fixture(scope="session")
def api_key(request: SubRequest) -> str:
    try:
        return str(request.config.getoption("--stripe-secret-key"))
    except ValueError:
        pytest.skip()


@pytest.fixture()
def api_consumer(api_key: str) -> ApiConsumer:
    return ApiConsumer(api_key, "")


@pytest.fixture(scope="session")
def source(api_key: str) -> str:
    response = requests.post(
        f"{Request.url}/v1/tokens",
        auth=(api_key, ""),
        data={
            "card[number]": "4242424242424242",  # test card number
            "card[exp_month]": "12",
            "card[exp_year]": str(datetime.now().year + 2),
            "card[cvc]": "123",
        },
    )
    assert response.ok
    return str(response.json()["id"])


@pytest.mark.stripe
def test_charge_then_capture(api_consumer: ApiConsumer, source: str, api_key: str) -> None:
    charge_id = api_consumer.charge(get_dollars("15.00"), source)
    api_consumer.capture(charge_id)

    response = requests.get(f"{Request.url}/v1/charges/{charge_id}", auth=(api_key, ""))
    capture_json = response.json()
    assert capture_json["amount"] == 1500  # cents
    assert capture_json["currency"] == "usd"
    assert capture_json["captured"]

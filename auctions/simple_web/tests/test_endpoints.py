import pytest
from flask import testing

from .. import app


@pytest.fixture()
def client() -> testing.FlaskClient:
    return app.test_client()


def test_returns_list_of_auctions(client: testing.FlaskClient) -> None:
    response = client.get("/", headers={"Content-type": "application/json"})

    assert response.status_code == 200
    assert type(response.json) == list


def test_return_single_auction(client: testing.FlaskClient) -> None:
    response = client.get("/1", headers={"Content-type": "application/json"})

    assert response.status_code == 200
    assert type(response.json) == dict


def test_places_bid(client: testing.FlaskClient) -> None:
    response = client.post("/1/bids", headers={"Content-type": "application/json"}, json={"amount": "15.99"})

    assert response.status_code == 200
    assert response.json == {"message": "Hooray! You are a winner"}

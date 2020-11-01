from datetime import datetime, timedelta

from flask.testing import FlaskClient
import pytest
from sqlalchemy.engine import Connection

from auctions_infrastructure import auctions


@pytest.fixture()
def example_auction(connection: Connection) -> int:
    """It should rather use a sequence of other API calls, maybe auctions'
    module use cases specific for creating an auction, not adding directly to the DB.
    """
    ends_at = datetime.now() + timedelta(days=3)
    result_proxy = connection.execute(
        auctions.insert(
            {"title": "Super aukcja", "starting_price": "0.99", "current_price": "1.00", "ends_at": ends_at}
        )
    )
    auction_id = result_proxy.lastrowid
    return int(auction_id)


def test_return_single_auction(client: FlaskClient, example_auction: int) -> None:
    response = client.get(f"/auctions/{example_auction}", headers={"Content-type": "application/json"})

    assert response.status_code == 200
    assert type(response.json) == dict


def test_returns_list_of_auctions(client: FlaskClient) -> None:
    response = client.get("/auctions/", headers={"Content-type": "application/json"})

    assert response.status_code == 200
    assert type(response.json) == list


@pytest.fixture()
def logged_in_client(client: FlaskClient) -> FlaskClient:
    email, password = "test+bid+1@cleanarchitecture.io", "Dumm123!"
    client.post(
        "/register",
        json={"email": email, "password": password},
    )
    return client


def test_places_bid(example_auction: int, logged_in_client: FlaskClient) -> None:
    response = logged_in_client.post(f"/auctions/{example_auction}/bids", json={"amount": "15.99"})

    assert response.status_code == 200
    assert response.json == {"message": "Hooray! You are a winner"}

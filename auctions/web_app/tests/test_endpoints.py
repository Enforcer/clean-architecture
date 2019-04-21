from datetime import datetime, timedelta
from typing import Generator

import inject
import pytest
from flask import testing, Flask
from sqlalchemy.engine import Connection

from auctions_infrastructure import auctions, bids

from ..app import create_app
from ..security import User


@pytest.fixture(scope="session")
def app() -> Flask:
    inject.clear()
    return create_app()


@pytest.fixture()
def client(app: Flask) -> testing.FlaskClient:
    return app.test_client()


@pytest.fixture(scope="session")
def sqlalchemy_connect_url(app: Flask) -> str:
    return app.config["DB_DSN"]


@pytest.fixture()
def remove_user(connection: Connection) -> Generator:
    yield
    connection.execute(User.__table__.delete(User.email == "test+register@cleanarchitecture.io"))


@pytest.fixture()
def create_remove_user(connection: Connection) -> Generator[str, None, None]:
    result_proxy = connection.execute(
        User.__table__.insert(
            # passwords are hashed automagically by Flask-security
            {"email": "test+login@cleanarchitecture.io", "password": "Dummy123!", "active": True}
        )
    )
    yield str(result_proxy.lastrowid)
    connection.execute(User.__table__.delete(User.email == "test+login@cleanarchitecture.io"))


def test_returns_list_of_auctions(client: testing.FlaskClient) -> None:
    response = client.get("/", headers={"Content-type": "application/json"})

    assert response.status_code == 200
    assert type(response.json) == list


@pytest.mark.usefixtures("remove_user")
def test_register(client: testing.FlaskClient) -> None:
    response = client.post(
        "/register",
        headers={"Content-type": "application/json"},
        json={"email": "test+register@cleanarchitecture.io", "password": "Dummy123!"},
    )

    assert response.status_code == 200
    json_response_body = response.json.copy()
    assert isinstance(json_response_body["response"]["user"].pop("authentication_token"), str)
    assert isinstance(json_response_body["response"]["user"].pop("id"), str)
    assert json_response_body == {"meta": {"code": 200}, "response": {"user": {}}}


def test_login(client: testing.FlaskClient, create_remove_user: str) -> None:
    response = client.post(
        "/login",
        headers={"Content-type": "application/json"},
        json={"email": "test+login@cleanarchitecture.io", "password": "Dummy123!"},
    )

    assert response.status_code == 200
    json_response_body = response.json.copy()
    json_response_body["response"]["user"].pop("authentication_token")
    assert json_response_body == {"meta": {"code": 200}, "response": {"user": {"id": create_remove_user}}}


@pytest.fixture()
def example_auction(connection: Connection) -> Generator[int, None, None]:
    ends_at = datetime.now() + timedelta(days=3)
    result_proxy = connection.execute(
        auctions.insert(
            {"title": "Super aukcja", "starting_price": "0.99", "current_price": "1.00", "ends_at": ends_at}
        )
    )
    auction_id = result_proxy.lastrowid
    connection.execute(bids.insert({"auction_id": auction_id, "amount": "1.00", "bidder_id": 1}))
    yield int(auction_id)
    connection.execute(bids.delete(bids.c.auction_id == auction_id))
    connection.execute(auctions.delete(auctions.c.id == auction_id))


def test_return_single_auction(client: testing.FlaskClient, example_auction: int) -> None:
    response = client.get(f"/{example_auction}", headers={"Content-type": "application/json"})

    assert response.status_code == 200
    assert type(response.json) == dict


def test_places_bid(client: testing.FlaskClient, example_auction: int) -> None:
    response = client.post(
        f"/{example_auction}/bids", headers={"Content-type": "application/json"}, json={"amount": "15.99"}
    )

    assert response.status_code == 200
    assert response.json == {"message": "Hooray! You are a winner"}

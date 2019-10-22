from datetime import datetime, timedelta
import os
from typing import Generator

from _pytest.tmpdir import TempPathFactory
from flask import Flask, testing
import pytest
from sqlalchemy.engine import Connection, create_engine

from auctions_infrastructure import auctions, bids
from customer_relationship.models import customers
from web_app.app import create_app
from web_app.security import User


@pytest.fixture(scope="module")
def config_path(tmp_path_factory: TempPathFactory) -> str:
    temp_dir = tmp_path_factory.mktemp("config")
    db_dir = tmp_path_factory.mktemp("test_db")
    conf_file_path = temp_dir / ".test_env_file"
    with open(conf_file_path, "w") as f:
        f.writelines(
            [
                "PAYMENTS_LOGIN=empty\n",
                "PAYMENTS_PASSWORD=empty\n",
                "EMAIL_HOST=localhost\n",
                "EMAIL_PORT=2525\n",
                "EMAIL_USERNAME=none\n",
                "EMAIL_PASSWORD=none\n",
                "EMAIL_FROM_NAME=Auctions\n",
                "EMAIL_FROM_ADDRESS=auctions@cleanarchitecture.io\n",
                "REDIS_HOST=localhost\n",
                f"DB_DSN=sqlite:///{db_dir}/db.sqlite\n",
            ]
        )
    return str(conf_file_path)


@pytest.fixture(scope="module")
def app(config_path: str) -> Flask:
    os.environ["CONFIG_PATH"] = config_path
    return create_app()


@pytest.fixture()
def client(app: Flask) -> testing.FlaskClient:
    return app.test_client()


@pytest.fixture()
def connection(app: Flask) -> Connection:
    engine = create_engine(os.environ["DB_DSN"])
    yield engine.connect()
    engine.dispose()


@pytest.fixture()
def remove_user(connection: Connection) -> Generator:
    yield
    connection.execute(User.__table__.delete(User.email == "test+register@cleanarchitecture.io"))
    connection.execute(customers.delete(customers.c.email == "test+register@cleanarchitecture.io"))


@pytest.fixture()
def create_remove_user(connection: Connection) -> Generator[str, None, None]:
    email = "test+login@cleanarchitecture.io"
    password = "Dummy123!"
    connection.execute(User.__table__.delete(User.email == email))
    connection.execute(customers.delete(customers.c.email == email))
    result_proxy = connection.execute(
        User.__table__.insert(
            # passwords are hashed automagically by Flask-security
            {"email": email, "password": password, "active": True}
        )
    )
    connection.execute(customers.insert({"id": result_proxy.lastrowid, "email": email}))
    yield str(result_proxy.lastrowid)
    connection.execute(User.__table__.delete(User.email == email))
    connection.execute(customers.delete(customers.c.email == email))


@pytest.fixture()
def another_user(connection: Connection) -> Generator[str, None, None]:
    email = "test+bidder@cleanarchitecture.io"
    password = "Dummy123!"
    result_proxy = connection.execute(
        User.__table__.insert(
            # passwords are hashed automagically by Flask-security
            {"email": email, "password": password, "active": True}
        )
    )
    connection.execute(customers.insert({"id": result_proxy.lastrowid, "email": email}))
    yield str(result_proxy.lastrowid)
    connection.execute(User.__table__.delete(User.email == email))
    connection.execute(customers.delete(customers.c.email == email))


@pytest.fixture()
def logged_in_user(create_remove_user: str, client: testing.FlaskClient) -> None:
    with client.session_transaction() as session:  # type: ignore
        session["user_id"] = create_remove_user
        session["_fresh"] = True


@pytest.mark.usefixtures("remove_user")
def test_register(client: testing.FlaskClient, connection: Connection) -> None:
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
    assert_customer_with_given_email_exists(connection, "test+register@cleanarchitecture.io")


def assert_customer_with_given_email_exists(connection: Connection, email: str) -> None:
    assert connection.execute(customers.select().where(customers.c.email == email)).first()


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
def example_auction(connection: Connection, another_user: str) -> Generator[int, None, None]:
    ends_at = datetime.now() + timedelta(days=3)
    result_proxy = connection.execute(
        auctions.insert(
            {"title": "Super aukcja", "starting_price": "0.99", "current_price": "1.00", "ends_at": ends_at}
        )
    )
    auction_id = result_proxy.lastrowid
    connection.execute(bids.insert({"auction_id": auction_id, "amount": "1.00", "bidder_id": another_user}))
    yield int(auction_id)
    connection.execute(bids.delete(bids.c.auction_id == auction_id))
    connection.execute(auctions.delete(auctions.c.id == auction_id))


def test_return_single_auction(client: testing.FlaskClient, example_auction: int) -> None:
    response = client.get(f"/auctions/{example_auction}", headers={"Content-type": "application/json"})

    assert response.status_code == 200
    assert type(response.json) == dict


def test_returns_list_of_auctions(client: testing.FlaskClient) -> None:
    response = client.get("/auctions/", headers={"Content-type": "application/json"})

    assert response.status_code == 200
    assert type(response.json) == list


@pytest.mark.usefixtures("logged_in_user")
def test_places_bid(client: testing.FlaskClient, example_auction: int) -> None:
    response = client.post(
        f"/auctions/{example_auction}/bids", headers={"Content-type": "application/json"}, json={"amount": "15.99"}
    )

    assert response.status_code == 200
    assert response.json == {"message": "Hooray! You are a winner"}

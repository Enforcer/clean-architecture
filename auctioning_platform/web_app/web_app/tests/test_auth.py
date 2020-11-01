from dataclasses import dataclass

from flask import testing
import pytest
from sqlalchemy.engine import Connection

from customer_relationship import customers


def test_register_returns_details_with_auth_token(client: testing.FlaskClient) -> None:
    response = client.post("/register", json={"email": "test+register@cleanarchitecture.io", "password": "Dummy123!"})

    assert response.status_code == 200
    json_response_body = response.json.copy()
    assert isinstance(json_response_body["response"]["user"].pop("authentication_token"), str)
    assert isinstance(json_response_body["response"]["user"].pop("id"), str)
    assert json_response_body == {"meta": {"code": 200}, "response": {"user": {}}}


def test_register_creates_customer(client: testing.FlaskClient, connection: Connection) -> None:
    response = client.post(
        "/register", json={"email": "test+register+123@cleanarchitecture.io", "password": "Dummy123!"}
    )
    assert response.status_code == 200

    assert_customer_with_given_email_exists(connection, "test+register@cleanarchitecture.io")


def assert_customer_with_given_email_exists(connection: Connection, email: str) -> None:
    assert connection.execute(customers.select().where(customers.c.email == email)).first()


@dataclass
class RegisteredUser:
    email: str
    password: str
    id: str


@pytest.fixture()
def registered_user(client: testing.FlaskClient) -> RegisteredUser:
    response = client.post("/register", json={"email": "test+login@cleanarchitecture.io", "password": "Dummy123!"})
    client.cookie_jar.clear()
    return RegisteredUser(
        email="test+login@cleanarchitecture.io", password="Dummy123!", id=response.json["response"]["user"]["id"]
    )


def test_login(client: testing.FlaskClient, registered_user: RegisteredUser) -> None:
    response = client.post("/login", json={"email": registered_user.email, "password": registered_user.password})

    assert response.status_code == 200
    json_response_body = response.json.copy()
    json_response_body["response"]["user"].pop("authentication_token")
    assert json_response_body == {
        "meta": {"code": 200},
        "response": {"user": {"id": registered_user.id}},
    }

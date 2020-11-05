import factory
from flask.testing import FlaskClient
import injector
import pytest

from foundation.value_objects.factories import get_dollars

from auctions import BeginningAuction, BeginningAuctionInputDto
from main.modules import RequestScope


class BeginningAuctionInputDtoFactory(factory.Factory):
    class Meta:
        model = BeginningAuctionInputDto

    auction_id = factory.Sequence(lambda n: n)
    title = factory.Faker("name")
    starting_price = get_dollars("0.99")
    ends_at = factory.Faker("future_datetime", end_date="+7d")


@pytest.fixture()
def example_auction(container: injector.Injector) -> int:
    """It should rather use a sequence of other API calls, maybe auctions'
    module use cases specific for creating an auction, not adding directly to the DB.
    """
    with container.get(RequestScope):
        uc = container.get(BeginningAuction)
        dto = BeginningAuctionInputDtoFactory.build()
        uc.execute(dto)

    return int(dto.auction_id)


def test_return_single_auction(client: FlaskClient, example_auction: int) -> None:
    """
    Returns a json - rpc client.

    Args:
        client: (todo): write your description
        example_auction: (todo): write your description
    """
    response = client.get(f"/auctions/{example_auction}", headers={"Content-type": "application/json"})

    assert response.status_code == 200
    assert type(response.json) == dict


def test_returns_list_of_auctions(client: FlaskClient) -> None:
    """
    Return a list of all cross - cases

    Args:
        client: (todo): write your description
    """
    response = client.get("/auctions/", headers={"Content-type": "application/json"})

    assert response.status_code == 200
    assert type(response.json) == list


@pytest.fixture()
def logged_in_client(client: FlaskClient) -> FlaskClient:
    """
    Authenticate with a client.

    Args:
        client: (todo): write your description
    """
    email, password = "test+bid+1@cleanarchitecture.io", "Dumm123!"
    client.post(
        "/register",
        json={"email": email, "password": password},
    )
    return client


def test_places_bid(example_auction: int, logged_in_client: FlaskClient) -> None:
    """
    Makes a single test for a given example.

    Args:
        example_auction: (todo): write your description
        logged_in_client: (todo): write your description
    """
    response = logged_in_client.post(f"/auctions/{example_auction}/bids", json={"amount": "15.99"})

    assert response.status_code == 200
    assert response.json == {"message": "Hooray! You are a winner"}

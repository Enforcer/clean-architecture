from decimal import Decimal

import inject
import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from web.apps import inject_config
from auctions_infrastructure.models import (
    Auction,
    Bid,
)


UserModel = get_user_model()


@pytest.fixture()
def other_user() -> UserModel:
    return UserModel.objects.create_user(username='nevermind', password='irrelevant')


@pytest.fixture()
def authenticated_client(client: Client) -> Client:
    username = 'bidderman'
    password = 'king'
    UserModel.objects.create_user(username=username, password=password)
    client.login(username=username, password=password)
    return client


@pytest.fixture()
def auction_without_bids() -> Auction:
    return Auction.objects.create(
        title='Cool socks',
        starting_price=Decimal('1.00'),
        current_price=Decimal('1.00'),
    )


@pytest.fixture()
def auction_with_one_bid(auction_without_bids: Auction, other_user: UserModel) -> Auction:
    bid = Bid.objects.create(
        amount=Decimal('10.00'),
        bidder=other_user,
        auction=auction_without_bids
    )
    auction_without_bids.current_price = bid.amount
    auction_without_bids.save()
    return auction_without_bids


@pytest.fixture(autouse=True)
def dependency_injection_config() -> None:
    inject.clear_and_configure(inject_config)

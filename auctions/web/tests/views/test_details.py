import pytest
from django.test import Client
from django.urls import reverse

from web.models import Auction


@pytest.mark.usefixtures('transactional_db')
def test_should_show_current_price(
        authenticated_client: Client, auction_without_bids: Auction
) -> None:
    url = reverse('details', args=[auction_without_bids.pk])
    expected_current_price = auction_without_bids.current_price
    response = authenticated_client.get(url)

    assert str(expected_current_price) in response.content.decode()

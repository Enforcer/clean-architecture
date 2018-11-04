import json
from decimal import Decimal

import pytest
from django.http import HttpResponse
from django.test import Client
from django.urls import reverse


from auctions_infrastructure.models import Auction


@pytest.mark.usefixtures('transactional_db')
def test_should_win_auction_when_someone_else_with_less_amount_bidded_before(
        authenticated_client: Client, auction_with_one_bid: Auction
) -> None:
    url = reverse('make_a_bid', args=[auction_with_one_bid.pk])
    expected_current_price = auction_with_one_bid.current_price * 2
    data = json.dumps({
        'amount': str(expected_current_price)
    })
    response = authenticated_client.post(url, data, content_type='application/json')

    assert_wins_with_current_price(response, expected_current_price)


def assert_wins_with_current_price(response: HttpResponse, expected_price: Decimal) -> None:
    decoded_body = response.content.decode()
    assert ':)' in decoded_body, f'Bidder is not a winner! - "{decoded_body}"'
    assert f'Current price is {expected_price}' in decoded_body, f'"Current price differs! "{decoded_body}"'

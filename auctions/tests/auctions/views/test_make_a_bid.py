import json
from decimal import Decimal

import pytest
from django.http import HttpResponse
from django.test import Client
from django.urls import reverse


from auctions.models import Auction


def assert_wins_with_current_price(response: HttpResponse, expected_price: Decimal) -> None:
    decoded_body = response.content.decode()
    assert ':)' in decoded_body, f'Bidder is not a winner! - "{decoded_body}"'
    assert f'Current price is {expected_price}' in decoded_body, f'"Current price differs! "{decoded_body}"'


def assert_loses_with_current_price(response: HttpResponse, expected_price: Decimal) -> None:
    decoded_body = response.content.decode()
    assert ':(' in decoded_body, f'Bidder is not a winner! - "{decoded_body}"'
    assert f'Current price is {expected_price}' in decoded_body, f'"Current price differs! "{decoded_body}"'


@pytest.mark.usefixtures('transactional_db')
def test_should_win_auction_when_no_one_else_is_bidding(
        authenticated_client: Client, auction_without_bids: Auction
) -> None:
    pytest.skip('Testing via views is a scam')
    url = reverse('make_a_bid', args=[auction_without_bids.pk])
    expected_current_price = auction_without_bids.current_price * 10
    data = json.dumps({
        'amount': str(expected_current_price)
    })
    response = authenticated_client.post(url, data, content_type='application/json')

    assert_wins_with_current_price(response, expected_current_price)


@pytest.mark.usefixtures('transactional_db')
def test_should_not_be_winning_if_bid_lower_than_current_price(
        authenticated_client: Client, auction_without_bids: Auction
) -> None:
    pytest.skip('Testing via views is a scam')
    url = reverse('make_a_bid', args=[auction_without_bids.pk])
    bid_price = auction_without_bids.current_price - Decimal('1.00')
    data = json.dumps({
        'amount': str(bid_price)
    })
    response = authenticated_client.post(url, data, content_type='application/json')

    assert_loses_with_current_price(response, auction_without_bids.current_price)


@pytest.mark.usefixtures('transactional_db')
def test_should_win_auction_when_someone_else_with_less_amount_bidded_before(
        authenticated_client: Client, auction_with_one_bid: Auction
) -> None:
    pytest.skip('Testing via views is a scam')
    url = reverse('make_a_bid', args=[auction_with_one_bid.pk])
    expected_current_price = auction_with_one_bid.current_price * 2
    data = json.dumps({
        'amount': str(expected_current_price)
    })
    response = authenticated_client.post(url, data, content_type='application/json')

    assert_wins_with_current_price(response, expected_current_price)

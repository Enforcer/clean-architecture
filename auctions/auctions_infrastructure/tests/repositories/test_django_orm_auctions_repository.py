from datetime import datetime
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from auctions.domain.entities import (
    Auction,
    Bid,
)
from auctions.domain.factories import get_dollars
from auctions_infrastructure.repositories import DjangoORMAuctionsRepository
from auctions_infrastructure.models import (
    Auction as AuctionModel,
    Bid as BidModel,
)


UserModel = get_user_model()


@pytest.fixture()
def bidder() -> UserModel:
    return UserModel.objects.create()


@pytest.fixture()
def winning_bid_amount() -> Decimal:
    return Decimal('15.00')


@pytest.fixture()
def auction_model_with_a_bid(winning_bid_amount: Decimal, bidder: UserModel, ends_at: datetime) -> AuctionModel:
    auction = AuctionModel.objects.create(
        title='Cool socks',
        starting_price=winning_bid_amount / 2,
        current_price=winning_bid_amount,
        ends_at=ends_at,
    )
    BidModel.objects.create(
        bidder_id=bidder.id,
        amount=winning_bid_amount,
        auction=auction
    )
    return auction


@pytest.mark.usefixtures('transactional_db')
def test_gets_existing_auction(
        auction_model_with_a_bid: AuctionModel, winning_bid_amount: Decimal, ends_at: datetime) -> None:
    auction = DjangoORMAuctionsRepository().get(auction_model_with_a_bid.id)

    assert auction.id == auction_model_with_a_bid.id
    assert auction.title == auction_model_with_a_bid.title
    assert auction.starting_price == get_dollars(auction_model_with_a_bid.starting_price)
    assert auction.current_price == get_dollars(winning_bid_amount)
    assert auction.ends_at == ends_at


@pytest.mark.usefixtures('transactional_db')
def test_saves_auction_changes(auction_model_with_a_bid: AuctionModel, ends_at: datetime) -> None:
    bid_model = auction_model_with_a_bid.bid_set.first()
    auction = Auction(
        id=auction_model_with_a_bid.id,
        title=auction_model_with_a_bid.title,
        starting_price=get_dollars(auction_model_with_a_bid.starting_price),
        ends_at=ends_at,
        bids=[
            Bid(bid_model.id, bid_model.bidder_id, get_dollars(bid_model.amount)),
            Bid(None, bid_model.bidder_id, get_dollars(bid_model.amount))
        ]
    )

    DjangoORMAuctionsRepository().save(auction)

    assert auction_model_with_a_bid.bid_set.count() == 2


@pytest.mark.usefixtures('transactional_db')
def test_removes_withdrawn_bids(auction_model_with_a_bid: AuctionModel, ends_at: datetime) -> None:
    bid_model = auction_model_with_a_bid.bid_set.first()
    auction = Auction(
        id=auction_model_with_a_bid.id,
        title=auction_model_with_a_bid.title,
        starting_price=get_dollars(auction_model_with_a_bid.starting_price),
        ends_at=ends_at,
        bids=[
            Bid(bid_model.id, bid_model.bidder_id, get_dollars(bid_model.amount)),
        ]
    )
    auction.withdraw_bids([bid_model.id])

    DjangoORMAuctionsRepository().save(auction)

    assert auction_model_with_a_bid.bid_set.count() == 0

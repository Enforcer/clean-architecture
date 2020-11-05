from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock

import pytest
from sqlalchemy import func, select
from sqlalchemy.engine import Connection, Engine, RowProxy

from foundation.events import Event, EventBus
from foundation.value_objects.factories import get_dollars

from auctions.domain.entities import Auction, Bid
from auctions_infrastructure import auctions, bids
from auctions_infrastructure.repositories import SqlAlchemyAuctionsRepo
from db_infrastructure import Base


@pytest.fixture(scope="session")
def sqlalchemy_connect_url() -> str:
    """
    Return the sqlalchemy sqlalchemy url.

    Args:
    """
    return "sqlite:///:memory:"


@pytest.fixture(scope="session", autouse=True)
def setup_teardown_tables(engine: Engine) -> None:
    """
    Setup all tables.

    Args:
        engine: (todo): write your description
    """
    Base.metadata.create_all(engine)


@pytest.fixture()
def winning_bid_amount() -> Decimal:
    """
    Winning amount.

    Args:
    """
    return Decimal("15.00")


@pytest.fixture()
def bidder_id(connection: Connection) -> int:
    """
    Return a connection object id from a connection.

    Args:
        connection: (todo): write your description
    """
    return 1


@pytest.fixture()
def another_bidder_id() -> int:
    """
    Returns the integer id of the int.

    Args:
    """
    return 2


@pytest.fixture()
def expired_auction(connection: Connection, past_date: datetime) -> RowProxy:
    """
    Checks if there is a expired.

    Args:
        connection: (todo): write your description
        past_date: (todo): write your description
    """
    connection.execute(
        auctions.insert().values(
            {
                "id": 0,
                "title": "Nothing interesting",
                "starting_price": Decimal("1.99"),
                "current_price": Decimal("1.99"),
                "ends_at": past_date,
                "ended": False,
            }
        )
    )
    return connection.execute(auctions.select(whereclause=auctions.c.id == 0)).first()


@pytest.fixture()
def auction_model_with_a_bid(
    connection: Connection, winning_bid_amount: Decimal, bidder_id: int, ends_at: datetime
) -> RowProxy:
    """
    Make an instance of the given connection.

    Args:
        connection: (todo): write your description
        winning_bid_amount: (todo): write your description
        bidder_id: (str): write your description
        ends_at: (todo): write your description
    """
    connection.execute(
        auctions.insert().values(
            {
                "id": 1,
                "title": "Cool socks",
                "starting_price": winning_bid_amount / 2,
                "current_price": winning_bid_amount,
                "ends_at": ends_at,
                "ended": False,
            }
        )
    )
    connection.execute(bids.insert().values({"amount": winning_bid_amount, "auction_id": 1, "bidder_id": bidder_id}))
    return connection.execute(auctions.select(whereclause=auctions.c.id == 1)).first()


@pytest.fixture()
def bid_model(connection: Connection, auction_model_with_a_bid: RowProxy) -> RowProxy:
    """
    Return the model instance of the database.

    Args:
        connection: (todo): write your description
        auction_model_with_a_bid: (todo): write your description
    """
    return connection.execute(bids.select().where(bids.c.auction_id == auction_model_with_a_bid.id)).first()


@pytest.mark.usefixtures("transaction")
def test_gets_existing_auction(
    connection: Connection,
    auction_model_with_a_bid: RowProxy,
    bid_model: RowProxy,
    ends_at: datetime,
    event_bus_mock: Mock,
) -> None:
    """
    Test if you canction of a given connection

    Args:
        connection: (todo): write your description
        auction_model_with_a_bid: (todo): write your description
        bid_model: (todo): write your description
        ends_at: (str): write your description
        event_bus_mock: (todo): write your description
    """
    auction = SqlAlchemyAuctionsRepo(connection, event_bus_mock).get(auction_model_with_a_bid.id)

    assert auction.id == auction_model_with_a_bid.id
    assert auction.title == auction_model_with_a_bid.title
    assert auction.starting_price == get_dollars(auction_model_with_a_bid.starting_price)
    assert auction.current_price == get_dollars(bid_model.amount)
    assert auction.ends_at == ends_at
    assert set(auction.bids) == {Bid(bid_model.id, bid_model.bidder_id, get_dollars(bid_model.amount))}


@pytest.mark.usefixtures("transaction")
def test_saves_auction_changes(
    connection: Connection,
    another_bidder_id: int,
    bid_model: RowProxy,
    auction_model_with_a_bid: RowProxy,
    ends_at: datetime,
    event_bus_mock: Mock,
) -> None:
    """
    This function is called when a new changes have changed.

    Args:
        connection: (todo): write your description
        another_bidder_id: (str): write your description
        bid_model: (todo): write your description
        auction_model_with_a_bid: (todo): write your description
        ends_at: (todo): write your description
        event_bus_mock: (todo): write your description
    """
    new_bid_price = get_dollars(bid_model.amount * 2)
    auction = Auction(
        id=auction_model_with_a_bid.id,
        title=auction_model_with_a_bid.title,
        starting_price=get_dollars(auction_model_with_a_bid.starting_price),
        ends_at=ends_at,
        bids=[
            Bid(bid_model.id, bid_model.bidder_id, get_dollars(bid_model.amount)),
            Bid(None, another_bidder_id, new_bid_price),
        ],
        ended=True,
    )

    SqlAlchemyAuctionsRepo(connection, event_bus_mock).save(auction)

    assert connection.execute(select([func.count()]).select_from(bids)).scalar() == 2
    proxy = connection.execute(select([auctions]).where(auctions.c.id == auction_model_with_a_bid.id)).first()
    assert proxy.current_price == new_bid_price.amount
    assert proxy.ended


@pytest.mark.usefixtures("transaction")
def test_removes_withdrawn_bids(
    connection: Connection, bid_model: RowProxy, auction_model_with_a_bid: dict, ends_at: datetime, event_bus_mock: Mock
) -> None:
    """
    Test if a new bus hasdrawn.

    Args:
        connection: (todo): write your description
        bid_model: (str): write your description
        auction_model_with_a_bid: (todo): write your description
        ends_at: (todo): write your description
        event_bus_mock: (todo): write your description
    """
    auction = Auction(
        id=auction_model_with_a_bid.id,
        title=auction_model_with_a_bid.title,
        starting_price=get_dollars(auction_model_with_a_bid.starting_price),
        ends_at=ends_at,
        bids=[Bid(bid_model.id, bid_model.bidder_id, get_dollars(bid_model.amount))],
        ended=False,
    )
    auction.withdraw_bids([bid_model.id])

    SqlAlchemyAuctionsRepo(connection, event_bus_mock).save(auction)

    assert connection.execute(select([func.count()]).select_from(bids)).scalar() == 0


@pytest.mark.usefixtures("transaction")
def test_AuctionsRepo_UponSavingAuction_PostsPendingEventsViaEventBus(
    connection: Connection, another_bidder_id: int, auction_model_with_a_bid: RowProxy, event_bus_mock: Mock
) -> None:
    """
    Test for pending pending pending pending pending pending pending pending pending notifications.

    Args:
        connection: (todo): write your description
        another_bidder_id: (int): write your description
        auction_model_with_a_bid: (todo): write your description
        event_bus_mock: (todo): write your description
    """
    repo = SqlAlchemyAuctionsRepo(connection, event_bus_mock)
    auction = repo.get(auction_model_with_a_bid.id)
    auction.place_bid(another_bidder_id, auction.current_price + get_dollars("1.00"))

    repo.save(auction)

    event_bus_mock.post.assert_called()


class EventBusStub(EventBus):
    def __init__(self) -> None:
        """
        Initialize events.

        Args:
            self: (todo): write your description
        """
        self.events = []

    def post(self, event: Event) -> None:
        """
        Adds a new event.

        Args:
            self: (todo): write your description
            event: (todo): write your description
        """
        self.events.append(event)


@pytest.fixture()
def event_bus_stub() -> EventBusStub:
    """
    Return the event stubevent.

    Args:
    """
    return EventBusStub()


@pytest.mark.usefixtures("transaction")
def test_AuctionsRepo_UponSavingAuction_ClearsPendingEvents(
    connection: Connection, another_bidder_id: int, auction_model_with_a_bid: RowProxy, event_bus_mock: Mock
) -> None:
    """
    Test for pending pending pending pending pending pending pending pending pending pending notifications.

    Args:
        connection: (todo): write your description
        another_bidder_id: (int): write your description
        auction_model_with_a_bid: (todo): write your description
        event_bus_mock: (todo): write your description
    """
    repo = SqlAlchemyAuctionsRepo(connection, event_bus_mock)
    auction = repo.get(auction_model_with_a_bid.id)
    auction.place_bid(another_bidder_id, auction.current_price + get_dollars("1.00"))

    repo.save(auction)

    assert len(auction.domain_events) == 0


# @pytest.mark.usefixtures("transaction")
# def test_AuctionsRepo_UponSavingAuction_PostsPendingEventsViaEventBus(
#     connection: Connection, another_bidder_id: int, auction_model_with_a_bid: RowProxy, event_bus_stub: EventBusStub
# ) -> None:
#     repo = SqlAlchemyAuctionsRepo(connection, event_bus_stub)
#     auction = repo.get(auction_model_with_a_bid.id)
#     auction.place_bid(another_bidder_id, auction.current_price + get_dollars("1.00"))
#
#     repo.save(auction)
#
#     event_bus_stub.events

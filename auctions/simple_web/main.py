import threading
from datetime import (
    datetime,
    timedelta,
)

import inject
from flask import (
    Flask,
    request,
)
from pybuses import EventBus
from sqlalchemy.engine import (
    Connection,
    Engine,
)

from auctions.application.repositories import AuctionsRepository
from auctions.application.ports import PaymentProvider
from auctions.domain.entities import Auction
from auctions.domain.events import BidderHasBeenOverbid
from auctions.domain.factories import get_dollars
from auctions_infrastructure import setup as auctions_infrastructure_setup
from auctions_infrastructure.repositories.auctions import (
    InMemoryAuctionsRepository,
    SqlAlchemyAuctionsRepo,
)
# from auctions_infrastructure.adapters import CaPaymentsPaymentProvider


def setup(app: Flask) -> None:
    connection_provider = setup_db(app)
    setup_dependency_injection(connection_provider, {'payments.login': '', 'payments.password': ''})
    setup_event_subscriptions()


def setup_db(app: Flask) -> 'ThreadlocalConnectionProvider':
    engine = auctions_infrastructure_setup()
    connection_provider = ThreadlocalConnectionProvider(engine)

    @app.before_request
    def transaction_start() -> None:
        request.tx = connection_provider().begin()

    @app.after_request
    def transaction_commit(response: app.response_class) -> app.response_class:
        try:
            if hasattr(request, 'tx') and response.status_code < 400:
                request.tx.commit()
        finally:
            connection_provider.close_if_present()

        return response

    conn = engine.connect()
    conn.execute('''
        INSERT INTO auctions (id, title, starting_price, current_price, ends_at)
        VALUES(1, "Super aukcja", "0.99", "0.99", '2019-12-12 10:00:00')
    ''')
    conn.close()

    return connection_provider


def setup_dependency_injection(connection_provider: 'ThreadlocalConnectionProvider', settings: dict) -> None:
    def di_config(binder: inject.Binder) -> None:
        binder.bind_to_provider(Connection, connection_provider)
        binder.bind_to_provider(AuctionsRepository, SqlAlchemyAuctionsRepo)

        binder.bind(EventBus, EventBus())
        # binder.bind(
        #     PaymentProvider,
        #     CaPaymentsPaymentProvider(settings['payments.login'], settings['payments.password'])
        # )

    inject.configure(di_config)


class ThreadlocalConnectionProvider:

    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        self._storage = threading.local()

    def __call__(self) -> Connection:
        try:
            return self._storage.connection
        except AttributeError:
            connection = self._engine.connect()
            self._storage.connection = connection
            return connection

    def is_present(self) -> bool:
        return hasattr(self._storage, 'connection')

    def close_if_present(self) -> None:
        try:
            self._storage.connection.close()
            del self._storage.connection
        except AttributeError:
            pass


# send_email = object
# send_email.delay = lambda *args, **kwargs: None


def setup_event_subscriptions():
    event_bus = inject.instance(EventBus)

    # event_bus.subscribe(
    #     BidderHasBeenOverbid, lambda event: send_email.delay(event.auction_id, event.bidder_id, event.money.amount)
    # )

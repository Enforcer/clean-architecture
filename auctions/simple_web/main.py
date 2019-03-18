import os
import threading

import dotenv
import inject
from flask import Flask, request
from pybuses import EventBus
from sqlalchemy.engine import Connection, Engine

from auctions.application import queries as auction_queries
from auctions.application.ports import PaymentProvider
from auctions.application.repositories import AuctionsRepository
from auctions_infrastructure import queries as auctions_inf_queries, setup as auctions_infrastructure_setup
from auctions_infrastructure.adapters import CaPaymentsPaymentProvider
from auctions_infrastructure.repositories.auctions import SqlAlchemyAuctionsRepo
from customer_relationship import CustomerRelationshipConfig, CustomerRelationshipFacade


def setup(app: Flask) -> None:
    dotenv.load_dotenv(os.path.join(os.path.dirname(__file__), os.pardir, ".env_file"))
    settings = {
        "payments.login": os.environ["PAYMENTS_LOGIN"],
        "payments.password": os.environ["PAYMENTS_PASSWORD"],
        "email.host": os.environ["EMAIL_HOST"],
        "email.port": os.environ["EMAIL_PORT"],
        "email.username": os.environ["EMAIL_USERNAME"],
        "email.password": os.environ["EMAIL_PASSWORD"],
        "email.from.name": os.environ["EMAIL_FROM_NAME"],
        "email.from.address": os.environ["EMAIL_FROM_ADDRESS"],
    }
    connection_provider = setup_db(app)
    event_bus = EventBus()

    setup_dependency_injection(settings, connection_provider, event_bus)


def setup_db(app: Flask) -> "ThreadlocalConnectionProvider":
    engine = auctions_infrastructure_setup()
    connection_provider = ThreadlocalConnectionProvider(engine)

    @app.before_request
    def transaction_start() -> None:
        request.tx = connection_provider.open().begin()

    @app.after_request
    def transaction_commit(response: app.response_class) -> app.response_class:
        try:
            if hasattr(request, "tx") and response.status_code < 400:
                request.tx.commit()
        finally:
            connection_provider.close_if_present()

        return response

    conn = engine.connect()
    conn.execute(
        """
        INSERT INTO auctions (id, title, starting_price, current_price, ends_at)
        VALUES(1, "Super aukcja", "0.99", "0.99", '2019-12-12 10:00:00')
    """
    )
    conn.execute(
        """
        INSERT INTO bids (auction_id, amount, bidder_id)
        VALUES(1, '1.00', 1)
    """
    )
    conn.close()

    return connection_provider


def setup_dependency_injection(
    settings: dict, connection_provider: "ThreadlocalConnectionProvider", event_bus: EventBus
) -> None:
    cr_config = CustomerRelationshipConfig(
        email_host=settings["email.host"],
        email_port=int(settings["email.port"]),
        email_username=settings["email.username"],
        email_password=settings["email.password"],
        email_from=(settings["email.from.name"], settings["email.from.address"]),
    )
    CustomerRelationshipFacade(cr_config, event_bus)

    def di_config(binder: inject.Binder) -> None:
        binder.bind_to_provider(Connection, connection_provider)
        binder.bind_to_provider(AuctionsRepository, SqlAlchemyAuctionsRepo)

        binder.bind_to_provider(auction_queries.GetActiveAuctions, auctions_inf_queries.SqlGetActiveAuctions)
        binder.bind_to_provider(auction_queries.GetSingleAuction, auctions_inf_queries.SqlGetSingleAuction)

        binder.bind(EventBus, event_bus)
        binder.bind(
            PaymentProvider, CaPaymentsPaymentProvider(settings["payments.login"], settings["payments.password"])
        )

    inject.configure(di_config)


class ThreadlocalConnectionProvider:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        self._storage = threading.local()

    def __call__(self) -> Connection:
        try:
            return self._storage.connection
        except AttributeError:
            raise Exception("No connection available")

    def is_present(self) -> bool:
        return hasattr(self._storage, "connection")

    def open(self) -> Connection:
        assert not hasattr(self._storage, "connection")
        connection = self._engine.connect()
        self._storage.connection = connection
        return connection

    def close_if_present(self) -> None:
        try:
            self._storage.connection.close()
            del self._storage.connection
        except AttributeError:
            pass

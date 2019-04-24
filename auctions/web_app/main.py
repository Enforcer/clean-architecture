import os
import threading
from typing import Callable

import dotenv
import inject
from flask import Flask, request, Response
from pybuses import EventBus
from redis import Redis
from rq import Queue
from sqlalchemy import event as sa_event
from sqlalchemy.engine import Connection, Engine, create_engine
from sqlalchemy.orm import Session

from auctions.application import queries as auction_queries
from auctions.application.repositories import AuctionsRepository
from auctions_infrastructure import queries as auctions_inf_queries
from auctions_infrastructure.repositories.auctions import SqlAlchemyAuctionsRepo
from customer_relationship import CustomerRelationshipConfig, CustomerRelationshipFacade
from db_infrastructure import metadata

# Models has to be in one place to be discoverable for metadata.create_all
from web_app.security import User, Role, RolesUsers  # noqa
from auctions_infrastructure import auctions, bids, bidders  # noqa
from customer_relationship.models import customers  # noqa


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
    enqueue_in_rq = setup_rq()

    def enqueue_after_commit(fun: Callable, *args, **kwargs):
        def listener(_conn):
            enqueue_in_rq(fun, *args, **kwargs)

        sa_event.listen(inject.instance(Connection), "commit", listener, once=True)

    setup_contexts(settings, event_bus, enqueue_after_commit)
    setup_dependency_injection(settings, connection_provider, event_bus)


def setup_db(app: Flask) -> "ThreadlocalConnectionProvider":
    engine = create_engine(app.config["DB_DSN"], echo=True)
    connection_provider = ThreadlocalConnectionProvider(engine)

    @app.before_request
    def transaction_start() -> None:
        request.tx = connection_provider.open().begin()

    @app.after_request
    def transaction_commit(response: Response) -> Response:
        try:
            if hasattr(request, "tx") and response.status_code < 400:
                request.tx.commit()
        finally:
            connection_provider.close_if_present()

        return response

    # TODO: Use migrations for that
    metadata.create_all(engine)

    return connection_provider


def setup_rq() -> Callable:
    queue = Queue(connection=Redis())
    return queue.enqueue


def setup_contexts(settings: dict, event_bus: EventBus, enqueue_fun: Callable) -> None:
    cr_config = CustomerRelationshipConfig(
        email_host=settings["email.host"],
        email_port=int(settings["email.port"]),
        email_username=settings["email.username"],
        email_password=settings["email.password"],
        email_from=(settings["email.from.name"], settings["email.from.address"]),
    )
    cr_context = CustomerRelationshipFacade(cr_config, event_bus, enqueue_fun)

    @sa_event.listens_for(User, "after_insert")
    def insert_cb(_mapper, connection: Connection, user: User) -> None:
        cr_context.create_customer(connection, user.id, user.email)

    @sa_event.listens_for(User, "after_update")
    def update_cb(_mapper, connection: Connection, user: User) -> None:
        cr_context.update_customer(connection, user.id, user.email)


def setup_dependency_injection(
    settings: dict, connection_provider: "ThreadlocalConnectionProvider", event_bus: EventBus
) -> None:
    def di_config(binder: inject.Binder) -> None:
        binder.bind_to_provider(Connection, connection_provider)
        binder.bind_to_provider(Session, connection_provider.provide_session)
        binder.bind_to_provider(AuctionsRepository, SqlAlchemyAuctionsRepo)

        binder.bind_to_provider(auction_queries.GetActiveAuctions, auctions_inf_queries.SqlGetActiveAuctions)
        binder.bind_to_provider(auction_queries.GetSingleAuction, auctions_inf_queries.SqlGetSingleAuction)

        binder.bind(EventBus, event_bus)

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

    def provide_session(self) -> Session:
        if not self.connected:
            raise Exception("No connection available")

        return self._storage.session

    @property
    def connected(self) -> bool:
        return hasattr(self._storage, "connection")

    def open(self) -> Connection:
        assert not hasattr(self._storage, "connection")
        connection = self._engine.connect()
        self._storage.connection = connection
        self._storage.session = Session(bind=connection)
        return connection

    def close_if_present(self) -> None:
        try:
            self._storage.connection.close()
            del self._storage.connection
            del self._storage.session
        except AttributeError:
            pass

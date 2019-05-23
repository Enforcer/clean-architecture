import os
import threading

import dotenv
from flask import Flask, Response, request
from flask_injector import FlaskInjector
import injector
from redis import Redis
from rq import Queue
from sqlalchemy import event as sa_event
from sqlalchemy.engine import Connection, Engine, create_engine
from sqlalchemy.orm import Session

from foundation.events import Enqueue, EventBus, InjectorEventBus

from auctions import Auctions
from auctions_infrastructure import AuctionsInfrastructure
from customer_relationship import CustomerRelationship, CustomerRelationshipConfig, CustomerRelationshipFacade
from db_infrastructure import metadata
from payments import Payments, PaymentsConfig
from web_app.blueprints.auctions import AuctionsWeb
from web_app.security import User


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

    setup_contexts(app, settings, connection_provider)


def setup_db(app: Flask) -> "ThreadlocalConnectionProvider":
    engine = create_engine(app.config["DB_DSN"], echo=True)
    connection_provider = ThreadlocalConnectionProvider(engine)

    @app.before_request
    def transaction_start() -> None:
        request.tx = connection_provider.open().begin()
        request.session = connection_provider.provide_session()

    @app.after_request
    def transaction_commit(response: Response) -> Response:
        try:
            if hasattr(request, "tx") and response.status_code < 400:
                request.tx.commit()
        finally:
            connection_provider.close_if_present()

        return response

    # Models has to be imported for metadata.create_all to discover them
    from auctions_infrastructure import auctions, bids  # noqa
    from customer_relationship.models import customers  # noqa
    from web_app.security import Role, RolesUsers, User  # noqa

    # TODO: Use migrations for that
    metadata.create_all(engine)

    return connection_provider


def setup_contexts(app: Flask, settings: dict, connection_provider: "ThreadlocalConnectionProvider") -> None:
    di_container = injector.Injector(
        [
            Db(connection_provider),
            Rq(),
            EventBusMod(),
            Configs(settings),
            Auctions(),
            AuctionsInfrastructure(),
            CustomerRelationship(),
            Payments(),
            AuctionsWeb(),
        ],
        auto_bind=False,
    )

    @sa_event.listens_for(User, "after_insert")
    def insert_cb(_mapper, _connection: Connection, user: User) -> None:
        di_container.get(CustomerRelationshipFacade).create_customer(user.id, user.email)

    @sa_event.listens_for(User, "after_update")
    def update_cb(_mapper, _connection: Connection, user: User) -> None:
        di_container.get(CustomerRelationshipFacade).update_customer(user.id, user.email)

    FlaskInjector(app, injector=di_container)


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


class Db(injector.Module):
    def __init__(self, conn_provider: ThreadlocalConnectionProvider) -> None:
        self._conn_provider = conn_provider

    def configure(self, binder: injector.Binder) -> None:
        binder.bind(Connection, to=injector.CallableProvider(self._conn_provider))
        binder.bind(Session, to=self._conn_provider.provide_session)


class Rq(injector.Module):
    @injector.singleton
    @injector.provider
    def enqueue(self) -> Enqueue:
        queue = Queue(connection=Redis())
        return queue.enqueue


class EventBusMod(injector.Module):
    @injector.provider
    def event_bus(self, inj: injector.Injector) -> EventBus:
        return InjectorEventBus(inj)


class Configs(injector.Module):
    def __init__(self, settings: dict) -> None:
        self._settings = settings

    @injector.singleton
    @injector.provider
    def customer_relationship_config(self) -> CustomerRelationshipConfig:
        return CustomerRelationshipConfig(
            email_host=self._settings["email.host"],
            email_port=int(self._settings["email.port"]),
            email_username=self._settings["email.username"],
            email_password=self._settings["email.password"],
            email_from=(self._settings["email.from.name"], self._settings["email.from.address"]),
        )

    @injector.singleton
    @injector.provider
    def payments_config(self) -> PaymentsConfig:
        return PaymentsConfig(username=self._settings["payments.login"], password=self._settings["payments.password"])

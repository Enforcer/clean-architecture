import injector
from main.db import ThreadlocalConnectionProvider
from redis import Redis
from rq import Queue
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session

from foundation.events import Enqueue, EventBus, InjectorEventBus

from customer_relationship import CustomerRelationshipConfig
from payments import PaymentsConfig


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

import injector
from redis import Redis
from rq import Queue
from sqlalchemy import event as sqlalchemy_event
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session

from foundation.events import EventBus, InjectorEventBus, RunAsyncHandler
from foundation.locks import Lock, LockFactory

from customer_relationship import CustomerRelationshipConfig
from payments import PaymentsConfig

from main.async_handler_task import async_handler_generic_task
from main.db import ThreadlocalConnectionProvider
from main.redis import RedisLock


class Db(injector.Module):
    def __init__(self, conn_provider: ThreadlocalConnectionProvider) -> None:
        self._conn_provider = conn_provider

    def configure(self, binder: injector.Binder) -> None:
        binder.bind(Connection, to=injector.CallableProvider(self._conn_provider))  # type: ignore
        binder.bind(Session, to=self._conn_provider.provide_session)  # type: ignore


class RedisMod(injector.Module):
    def __init__(self, redis_host: str) -> None:
        self._redis_host = redis_host

    def configure(self, binder: injector.Binder) -> None:
        binder.bind(Redis, Redis(host=self._redis_host))  # type: ignore

    @injector.provider
    def lock(self, redis: Redis) -> LockFactory:
        def create_lock(name: str, timeout: int = 30) -> Lock:
            return RedisLock(redis, name, timeout)

        return create_lock


class Rq(injector.Module):
    @injector.singleton
    @injector.provider
    def queue(self, redis: Redis) -> Queue:
        queue = Queue(connection=redis)
        return queue

    @injector.provider
    def run_async_handler(self, queue: Queue, connection: Connection) -> RunAsyncHandler:
        def enqueue_after_commit(handler_cls, *args, **kwargs):  # type: ignore
            sqlalchemy_event.listens_for(connection, "commit")(
                lambda _conn: queue.enqueue(async_handler_generic_task, handler_cls, *args, **kwargs)
            )

        return enqueue_after_commit


class EventBusMod(injector.Module):
    @injector.provider
    def event_bus(self, inj: injector.Injector, run_async_handler: RunAsyncHandler) -> EventBus:
        return InjectorEventBus(inj, run_async_handler)


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

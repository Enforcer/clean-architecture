import threading
from typing import Type

import injector
from injector import Provider, T
from redis import Redis
from rq import Queue
from sqlalchemy import event as sqlalchemy_event
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.orm import Session

from foundation.events import EventBus, InjectorEventBus, RunAsyncHandler
from foundation.locks import Lock, LockFactory

from customer_relationship import CustomerRelationshipConfig
from main.async_handler_task import async_handler_generic_task
from main.redis import RedisLock
from payments import PaymentsConfig


class RequestScope(injector.Scope):
    REGISTRY_KEY = "RequestScopeRegistry"

    def configure(self) -> None:
        self._locals = threading.local()

    def enter(self) -> None:
        assert not hasattr(self._locals, self.REGISTRY_KEY)
        setattr(self._locals, self.REGISTRY_KEY, {})

    def exit(self) -> None:
        for key, provider in getattr(self._locals, self.REGISTRY_KEY).items():
            provider.get(self.injector).close()
            delattr(self._locals, repr(key))

        delattr(self._locals, self.REGISTRY_KEY)

    def __enter__(self) -> None:
        self.enter()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        self.exit()

    def get(self, key: Type[T], provider: Provider[T]) -> Provider[T]:
        try:
            return getattr(self._locals, repr(key))  # type: ignore
        except AttributeError:
            provider = injector.InstanceProvider(provider.get(self.injector))
            setattr(self._locals, repr(key), provider)
            try:
                registry = getattr(self._locals, self.REGISTRY_KEY)
            except AttributeError:
                raise Exception(f"{key} is request scoped, but no RequestScope entered!")
            registry[key] = provider
            return provider


request = injector.ScopeDecorator(RequestScope)


class Db(injector.Module):
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    @request
    @injector.provider
    def connection(self) -> Connection:
        return self._engine.connect()

    @request
    @injector.provider
    def session(self, connection: Connection) -> Session:
        return Session(bind=connection)


class RedisMod(injector.Module):
    def __init__(self, redis_host: str) -> None:
        self._redis_host = redis_host

    def configure(self, binder: injector.Binder) -> None:
        binder.bind(Redis, Redis(host=self._redis_host))

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

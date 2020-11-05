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
        """
        Configure the thread.

        Args:
            self: (todo): write your description
        """
        self._locals = threading.local()

    def enter(self) -> None:
        """
        Initialize this instance.

        Args:
            self: (todo): write your description
        """
        assert not hasattr(self._locals, self.REGISTRY_KEY)
        setattr(self._locals, self.REGISTRY_KEY, {})

    def exit(self) -> None:
        """
        Exit all registered providers.

        Args:
            self: (todo): write your description
        """
        for key, provider in getattr(self._locals, self.REGISTRY_KEY).items():
            provider.get(self.injector).close()
            delattr(self._locals, repr(key))

        delattr(self._locals, self.REGISTRY_KEY)

    def __enter__(self) -> None:
        """
        Called by the request.

        Args:
            self: (todo): write your description
        """
        self.enter()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """
        Exit the given exception.

        Args:
            self: (todo): write your description
            exc_type: (todo): write your description
            exc_val: (todo): write your description
            exc_tb: (todo): write your description
        """
        self.exit()

    def get(self, key: Type[T], provider: Provider[T]) -> Provider[T]:
        """
        Retrieves a provider.

        Args:
            self: (todo): write your description
            key: (todo): write your description
            provider: (todo): write your description
        """
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
        """
        Initialize the engine.

        Args:
            self: (todo): write your description
            engine: (todo): write your description
        """
        self._engine = engine

    @request
    @injector.provider
    def connection(self) -> Connection:
        """
        Return a connection to the sqlite server.

        Args:
            self: (todo): write your description
        """
        return self._engine.connect()

    @request
    @injector.provider
    def session(self, connection: Connection) -> Session:
        """
        Return a new session.

        Args:
            self: (todo): write your description
            connection: (todo): write your description
        """
        return Session(bind=connection)


class RedisMod(injector.Module):
    def __init__(self, redis_host: str) -> None:
        """
        Initialize a redis connection.

        Args:
            self: (todo): write your description
            redis_host: (str): write your description
        """
        self._redis_host = redis_host

    def configure(self, binder: injector.Binder) -> None:
        """
        Configure the redis connection.

        Args:
            self: (todo): write your description
            binder: (todo): write your description
            injector: (todo): write your description
            Binder: (todo): write your description
        """
        binder.bind(Redis, Redis(host=self._redis_host))

    @injector.provider
    def lock(self, redis: Redis) -> LockFactory:
        """
        Create a lock object.

        Args:
            self: (todo): write your description
            redis: (todo): write your description
        """
        def create_lock(name: str, timeout: int = 30) -> Lock:
            """
            Create a lock.

            Args:
                name: (str): write your description
                timeout: (int): write your description
            """
            return RedisLock(redis, name, timeout)

        return create_lock


class Rq(injector.Module):
    @injector.singleton
    @injector.provider
    def queue(self, redis: Redis) -> Queue:
        """
        Gets a queue.

        Args:
            self: (todo): write your description
            redis: (todo): write your description
        """
        queue = Queue(connection=redis)
        return queue

    @injector.provider
    def run_async_handler(self, queue: Queue, connection: Connection) -> RunAsyncHandler:
        """
        Run a handler.

        Args:
            self: (todo): write your description
            queue: (todo): write your description
            connection: (todo): write your description
        """
        def enqueue_after_commit(handler_cls, *args, **kwargs):  # type: ignore
            """
            Enqueues a handler.

            Args:
                handler_cls: (todo): write your description
            """
            sqlalchemy_event.listens_for(connection, "commit")(
                lambda _conn: queue.enqueue(async_handler_generic_task, handler_cls, *args, **kwargs)
            )

        return enqueue_after_commit


class EventBusMod(injector.Module):
    @injector.provider
    def event_bus(self, inj: injector.Injector, run_async_handler: RunAsyncHandler) -> EventBus:
        """
        Runs the event handler.

        Args:
            self: (todo): write your description
            inj: (todo): write your description
            injector: (todo): write your description
            Injector: (todo): write your description
            run_async_handler: (todo): write your description
        """
        return InjectorEventBus(inj, run_async_handler)


class Configs(injector.Module):
    def __init__(self, settings: dict) -> None:
        """
        Initialize settings.

        Args:
            self: (todo): write your description
            settings: (dict): write your description
        """
        self._settings = settings

    @injector.singleton
    @injector.provider
    def customer_relationship_config(self) -> CustomerRelationshipConfig:
        """
        Get customer settings.

        Args:
            self: (todo): write your description
        """
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
        """
        Get payload configuration.

        Args:
            self: (todo): write your description
        """
        return PaymentsConfig(username=self._settings["payments.login"], password=self._settings["payments.password"])

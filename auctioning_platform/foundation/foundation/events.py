import abc
from typing import Callable, Generic, List, Type, TypeVar

from injector import Injector, Provider, UnsatisfiedRequirement

T = TypeVar("T")


class Event:
    pass


class EventMixin:
    def __init__(self) -> None:
        self._pending_domain_events: List[Event] = []

    def _record_event(self, event: Event) -> None:
        self._pending_domain_events.append(event)

    @property
    def domain_events(self) -> List[Event]:
        return self._pending_domain_events[:]

    def clear_events(self) -> None:
        self._pending_domain_events.clear()


class Handler(Generic[T]):
    """Simple generic used to associate handlers with events using DI.

    e.g Handler[AuctionEnded].
    """

    pass


class AsyncHandler(Generic[T]):
    """An async counterpart of Handler[Event]."""

    pass


class EventHandlerProvider(Provider):
    """Useful for configuring bind for event handlers.

    Using DI for dispatching events to handlers requires ability to bind multiple
    handlers to a single key (Handler[Event]).
    """

    def __init__(self, cls: Type[T]) -> None:
        self._cls = cls

    def get(self, injector: Injector) -> List[T]:
        return [injector.create_object(self._cls)]


class AsyncEventHandlerProvider(Provider):
    """An async counterpart of EventHandlerProvider.

    In async, one does not need to actually construct the instance.
    It is enough to obtain class itself.
    """

    def __init__(self, cls: Type[T]) -> None:
        self._cls = cls

    def get(self, _injector: Injector) -> List[Type[T]]:
        return [self._cls]


class EventBus(abc.ABC):
    @abc.abstractmethod
    def post(self, event: Event) -> None:
        raise NotImplementedError


RunAsyncHandler = Callable[[AsyncHandler[T], T], None]


class InjectorEventBus(EventBus):
    """A simple Event Bus that leverages injector.

    It requires Injector to be created with auto_bind=False.
    Otherwise UnsatisfiedRequirement is not raised. Instead,
    TypeError is thrown due to usage of `Handler` and `AsyncHandler` generics.
    """

    def __init__(self, injector: Injector, run_async_handler: RunAsyncHandler) -> None:
        self._injector = injector
        self._run_async_handler = run_async_handler

    def post(self, event: Event) -> None:
        try:
            handlers = self._injector.get(Handler[type(event)])  # type: ignore
        except UnsatisfiedRequirement:
            pass
        else:
            assert isinstance(handlers, list)
            for handler in handlers:
                handler(event)

        try:
            async_handlers = self._injector.get(AsyncHandler[type(event)])  # type: ignore
        except UnsatisfiedRequirement:
            pass
        else:
            assert isinstance(async_handlers, list)
            for async_handler in async_handlers:
                self._run_async_handler(async_handler, event)

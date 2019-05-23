import abc
from typing import Generic, List, Type, TypeVar

from injector import Injector, Key, Provider, UnsatisfiedRequirement

T = TypeVar("T")


class Event:
    pass


class Handler(Generic[T]):
    """Simple generic used to associate handlers with events using DI.

    e.g Handler[AuctionEnded].
    """

    pass


class AsyncHandler(Generic[T]):
    """An async counterpart of Handler[Event]."""

    pass


class ClassProviderMulti(Provider):
    """Useful for configuring bind for event handlers.

    Using DI for dispatching events to handlers requires ability to bind multiple
    handlers to a single key (Handler[Event]).
    """

    def __init__(self, cls: Type[T]) -> None:
        self._cls = cls

    def get(self, injector: Injector) -> List[T]:
        return [injector.create_object(self._cls)]


class EventBus(abc.ABC):
    @abc.abstractmethod
    def post(self, event: Event) -> None:
        raise NotImplementedError


class InjectorEventBus(EventBus):
    """A simple Event Bus that leverages injector.

    It requires Injector to be created with auto_bind=False.
    Otherwise UnsatisfiedRequirement is not raised. Instead,
    TypeError is thrown due to usage of `Handler` and `AsyncHandler` generics.
    """

    def __init__(self, injector: Injector) -> None:
        self._injector = injector

    def post(self, event: Event) -> None:
        try:
            handlers = self._injector.get(Handler[type(Event)])
        except UnsatisfiedRequirement:
            pass
        else:
            assert isinstance(handlers, list)
            for handler in handlers:
                handler(event)

        try:
            async_handlers = self._injector.get(AsyncHandler[type(Event)])
        except UnsatisfiedRequirement:
            pass
        else:
            assert isinstance(async_handlers, list)
            raise NotImplementedError("Not supported YET.")
            # Now we use `enqueue` to run handler in the background.
            # enqueue will be also injected.
            # Enqueue will effectively just either run the generic task with handler path (module/class_name) and args
            # or will just enqueue the function itself (rq). The worker has to have the app context, to be able
            # to run injector and reconstruct handler


Enqueue = Key("enqueue_function")

from typing import (
    Callable,
    Dict,
    Type,
)

from foundation.event import Event


class EventBus:
    def __init__(self) -> None:
        self._events_to_handlers: Dict[Type[Event], Callable] = {}

    def emit(self, event: Event) -> None:
        pass

    def subscribe(self, event_cls: Type[Event], handler: Callable) -> None:
        pass

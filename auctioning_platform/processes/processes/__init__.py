from typing import Callable, Dict, List, Tuple, Type

import injector
from sqlalchemy.engine import Connection
from typing_extensions import Protocol

from foundation.events import AsyncEventHandlerProvider, AsyncHandler, Event

from customer_relationship import CustomerRelationshipFacade
from payments import PaymentsFacade
from processes.paying_for_won_item import PayingForWonItem, PayingForWonItemHandler
from processes.repository import ProcessManagerDataRepo

__all__ = [
    # module
    "Processes"
]


class Handler(Protocol):
    registry: Dict[Type, Callable]

    def __call__(self, event: Event) -> None:
        ...


class ProcessManager(Protocol):
    handle: Handler


class Processes(injector.Module):
    PM_HANDLERS: List[Tuple[Type[ProcessManager], Type[Handler]]] = [
        (PayingForWonItem, PayingForWonItemHandler)  # type: ignore
    ]

    @injector.provider
    def get_paying_for_won_item(
        self, payments: PaymentsFacade, customer_relationship: CustomerRelationshipFacade
    ) -> PayingForWonItem:
        return PayingForWonItem(payments, customer_relationship)

    @injector.provider
    def get_data_repo(self, connection: Connection) -> ProcessManagerDataRepo:
        return ProcessManagerDataRepo(connection)

    def configure(self, binder: injector.Binder) -> None:
        for pm, handler_cls in self.PM_HANDLERS:
            handled_events = [event for event in pm.handle.registry.keys() if issubclass(event, Event)]
            for event in handled_events:
                binder.multibind(AsyncHandler[event], to=AsyncEventHandlerProvider(handler_cls))

        return None

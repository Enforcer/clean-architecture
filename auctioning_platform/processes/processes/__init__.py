from typing import Callable, Dict, List, Tuple, Type

import injector
from sqlalchemy.engine import Connection
from typing_extensions import Protocol

from foundation.events import AsyncEventHandlerProvider, AsyncHandler, Event

from customer_relationship import CustomerRelationshipFacade
from payments import PaymentsFacade

from processes.paying_for_won_item import PayingForWonItemSaga, PayingForWonItemSagaHandler
from processes.repository import SagaDataRepo

__all__ = [
    # module
    "Processes"
]


class Handler(Protocol):
    registry: Dict[Type, Callable]

    def __call__(self, event: Event) -> None:
        ...


class Saga(Protocol):
    handle: Handler


class Processes(injector.Module):
    SAGAS_HANDLERS: List[Tuple[Type[Saga], Type[Handler]]] = [
        (PayingForWonItemSaga, PayingForWonItemSagaHandler)  # type: ignore
    ]

    @injector.provider
    def get_paying_for_won_item_saga(
        self, payments: PaymentsFacade, customer_relationship: CustomerRelationshipFacade
    ) -> PayingForWonItemSaga:
        return PayingForWonItemSaga(payments, customer_relationship)

    @injector.provider
    def get_saga_data_repo(self, connection: Connection) -> SagaDataRepo:
        return SagaDataRepo(connection)

    def configure(self, binder: injector.Binder) -> None:
        for saga, handler_cls in self.SAGAS_HANDLERS:
            handled_events = [event for event in saga.handle.registry.keys() if issubclass(event, Event)]
            for event in handled_events:
                binder.multibind(AsyncHandler[event], to=AsyncEventHandlerProvider(handler_cls))

        return None

import injector
from sqlalchemy.engine import Connection

from foundation.events import AsyncEventHandlerProvider, AsyncHandler, EventBus

from payments.config import PaymentsConfig
from payments.events import PaymentCaptured, PaymentCharged, PaymentFailed, PaymentStarted
from payments.facade import PaymentsFacade

__all__ = [
    # module
    "Payments",
    "PaymentsConfig",
    # facade
    "PaymentsFacade",
    # events
    "PaymentStarted",
    "PaymentCharged",
    "PaymentCaptured",
    "PaymentFailed",
]


class Payments(injector.Module):
    @injector.provider
    def facade(self, config: PaymentsConfig, connection: Connection, event_bus: EventBus) -> PaymentsFacade:
        """
        Return a new connection.

        Args:
            self: (todo): write your description
            config: (todo): write your description
            connection: (todo): write your description
            event_bus: (todo): write your description
        """
        return PaymentsFacade(config, connection, event_bus)

    def configure(self, binder: injector.Binder) -> None:
        """
        Configure the logging.

        Args:
            self: (todo): write your description
            binder: (todo): write your description
            injector: (todo): write your description
            Binder: (todo): write your description
        """
        binder.multibind(AsyncHandler[PaymentCharged], to=AsyncEventHandlerProvider(PaymentChargedHandler))


class PaymentChargedHandler:
    @injector.inject
    def __init__(self, facade: PaymentsFacade) -> None:
        """
        Initialize the internal state.

        Args:
            self: (todo): write your description
            facade: (todo): write your description
        """
        self._facade = facade

    def __call__(self, event: PaymentCharged) -> None:
        """
        Call a custom event to call the event.

        Args:
            self: (todo): write your description
            event: (todo): write your description
        """
        self._facade.capture(event.payment_uuid, event.customer_id)

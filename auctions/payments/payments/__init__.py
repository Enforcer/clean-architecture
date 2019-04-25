from pybuses import EventBus

from foundation.value_objects import Money

from payments.api import ApiConsumer
from payments.config import PaymentsConfig


class PaymentsFacade:
    def __init__(self, config: PaymentsConfig, event_bus: EventBus) -> None:
        self._api_consumer = ApiConsumer(config.username, config.password)

        # event_bus.subscribe()

    def get_pending_payments(self, customer_id: int) -> None:
        pass

    def record_new_pending_payment(self, customer_id: int, amount: Money, description: str) -> None:
        # this will react to an event
        pass

    def pay(self, customer_id: int, payment_id: int, token: str) -> None:
        pass

    def get_invoices(self, customer_id: int) -> None:
        pass

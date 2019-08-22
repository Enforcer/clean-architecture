from typing import List
from uuid import UUID

from sqlalchemy.engine import Connection

from foundation.events import EventBus
from foundation.value_objects import Money

from payments import dao
from payments.api import ApiConsumer, PaymentFailedError
from payments.config import PaymentsConfig
from payments.events import PaymentCaptured, PaymentCharged, PaymentFailed, PaymentStarted


class PaymentsFacade:
    def __init__(self, config: PaymentsConfig, connection: Connection, event_bus: EventBus) -> None:
        self._api_consumer = ApiConsumer(config.username, config.password)
        self._connection = connection
        self._event_bus = event_bus

    def get_pending_payments(self, customer_id: int) -> List[dao.PaymentDto]:
        return dao.get_pending_payments(customer_id, self._connection)

    def start_new_payment(self, payment_uuid: UUID, customer_id: int, amount: Money, description: str) -> None:
        dao.start_new_payment(payment_uuid, customer_id, amount, description, self._connection)
        self._event_bus.post(PaymentStarted(payment_uuid, customer_id))

    def charge(self, payment_uuid: UUID, customer_id: int, token: str) -> None:
        payment = dao.get_payment(payment_uuid, customer_id, self._connection)
        if payment.status != dao.PaymentStatus.NEW.value:
            raise Exception(f"Can't pay - unexpected status {payment.status}")

        try:
            charge_id = self._api_consumer.charge(payment.amount, token)
        except PaymentFailedError:
            dao.update_payment(payment_uuid, customer_id, {"status": dao.PaymentStatus.FAILED.value}, self._connection)
            self._event_bus.post(PaymentFailed(payment_uuid, customer_id))
        else:
            update_values = {"status": dao.PaymentStatus.CHARGED.value, "charge_id": charge_id}
            dao.update_payment(payment_uuid, customer_id, update_values, self._connection)
            self._event_bus.post(PaymentCharged(payment_uuid, customer_id))

    def capture(self, payment_uuid: UUID, customer_id: int) -> None:
        charge_id = dao.get_payment_charge_id(payment_uuid, customer_id, self._connection)
        assert charge_id, f"No charge_id available for {payment_uuid}, aborting capture"
        self._api_consumer.capture(charge_id)
        dao.update_payment(payment_uuid, customer_id, {"status": dao.PaymentStatus.CAPTURED.value}, self._connection)
        self._event_bus.post(PaymentCaptured(payment_uuid, customer_id))

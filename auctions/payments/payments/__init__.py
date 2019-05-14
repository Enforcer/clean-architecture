from typing import Callable, List
from uuid import UUID

from sqlalchemy.engine import Connection

from foundation.value_objects import Money

from payments import dao
from payments.api import ApiConsumer, PaymentFailedError
from payments.config import PaymentsConfig

__all__ = ["PaymentsFacade"]


class PaymentsFacade:
    def __init__(self, config: PaymentsConfig, conn_provider: Callable[[], Connection]) -> None:
        self._api_consumer = ApiConsumer(config.username, config.password)
        self._conn_provider = conn_provider

    def get_pending_payments(self, customer_id: int) -> List[dao.PaymentDto]:
        return dao.get_pending_payments(customer_id, self._conn_provider())

    def start_new_payment(self, payment_uuid: UUID, customer_id: int, amount: Money, description: str) -> None:
        dao.start_new_payment(payment_uuid, customer_id, amount, description, self._conn_provider())

    def pay(self, payment_uuid: UUID, customer_id: int, token: str) -> None:
        payment = dao.get_payment(payment_uuid, customer_id, self._conn_provider())
        if payment.status != dao.PaymentStatus.NEW.value:
            raise Exception(f"Can't pay - unexpected status {payment.status}")

        try:
            charge_id = self._api_consumer.charge(payment.amount, token)
        except PaymentFailedError:
            dao.update_payment(
                payment_uuid, customer_id, {"status": dao.PaymentStatus.FAILED.value}, self._conn_provider()
            )
        else:
            update_values = {"status": dao.PaymentStatus.CHARGED.value, "charge_id": charge_id}
            dao.update_payment(payment_uuid, customer_id, update_values, self._conn_provider())

    def capture_payment(self, payment_uuid: UUID, customer_id: int) -> None:
        charge_id = dao.get_payment_charge_id(payment_uuid, customer_id, self._conn_provider())
        assert charge_id, f"No charge_id available for {payment_uuid}, aborting capture"
        self._api_consumer.capture(charge_id)
        dao.update_payment(
            payment_uuid, customer_id, {"status": dao.PaymentStatus.CAPTURED.value}, self._conn_provider()
        )

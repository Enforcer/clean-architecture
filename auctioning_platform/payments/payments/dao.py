from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Optional
from uuid import UUID

from sqlalchemy.engine import Connection

from foundation.value_objects import Money, factories

from payments.models import payments


class PaymentStatus(Enum):
    NEW = "NEW"
    CHARGED = "CHARGED"
    CAPTURED = "CAPTURED"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"


@dataclass
class PaymentDto:
    id: UUID
    amount: Money
    description: str
    status: str

    @classmethod
    def from_row(cls, row: Any) -> "PaymentDto":
        """
        Create a row from a row.

        Args:
            cls: (todo): write your description
            row: (todo): write your description
        """
        return PaymentDto(UUID(row.uuid), factories.get_dollars(row.amount / 100), row.description, row.status)


def start_new_payment(payment_uuid: UUID, customer_id: int, amount: Money, description: str, conn: Connection) -> None:
    """
    Start a new payment.

    Args:
        payment_uuid: (str): write your description
        customer_id: (str): write your description
        amount: (int): write your description
        description: (str): write your description
        conn: (todo): write your description
    """
    conn.execute(
        payments.insert(
            {
                "uuid": str(payment_uuid),
                "customer_id": customer_id,
                "amount": int(amount.amount) * 100,
                "currency": amount.currency.iso_code,
                "description": description,
                "status": PaymentStatus.NEW.value,
            }
        )
    )


def get_pending_payments(customer_id: int, conn: Connection) -> List[PaymentDto]:
    """
    Get pending pendingicas.

    Args:
        customer_id: (str): write your description
        conn: (todo): write your description
    """
    rows = conn.execute(
        payments.select((payments.c.customer_id == customer_id) & (payments.c.status == PaymentStatus.NEW.value))
    ).fetchall()
    return [PaymentDto.from_row(row) for row in rows]


def get_payment(payment_uuid: UUID, customer_id: int, conn: Connection) -> PaymentDto:
    """
    Return the payment.

    Args:
        payment_uuid: (str): write your description
        customer_id: (str): write your description
        conn: (todo): write your description
    """
    row = conn.execute(
        payments.select((payments.c.customer_id == customer_id) & (payments.c.uuid == str(payment_uuid)))
    ).first()
    return PaymentDto.from_row(row)


def get_payment_charge_id(payment_uuid: UUID, customer_id: int, conn: Connection) -> Optional[str]:
    """
    Get the charge id for a payment.

    Args:
        payment_uuid: (str): write your description
        customer_id: (str): write your description
        conn: (todo): write your description
    """
    row = conn.execute(
        payments.select((payments.c.customer_id == customer_id) & (payments.c.uuid == str(payment_uuid)))
    ).first()
    return str(row.charge_id) if row.charge_id else None


def update_payment(payment_uuid: UUID, customer_id: int, values: dict, conn: Connection) -> None:
    """
    Update the payment.

    Args:
        payment_uuid: (todo): write your description
        customer_id: (str): write your description
        values: (todo): write your description
        conn: (todo): write your description
    """
    conn.execute(
        payments.update()
        .where((payments.c.uuid == str(payment_uuid)) & (payments.c.customer_id == customer_id))
        .values(**values)
    )

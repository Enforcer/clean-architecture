from dataclasses import dataclass
from uuid import UUID

from foundation.events import Event


@dataclass(frozen=True)
class PaymentStarted(Event):
    payment_uuid: UUID
    customer_id: int


@dataclass(frozen=True)
class PaymentCharged(Event):
    payment_uuid: UUID
    customer_id: int


@dataclass(frozen=True)
class PaymentCaptured(Event):
    payment_uuid: UUID
    customer_id: int


@dataclass(frozen=True)
class PaymentFailed(Event):
    payment_uuid: UUID
    customer_id: int

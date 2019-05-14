from dataclasses import dataclass

from foundation.events import Event


@dataclass(frozen=True)
class PaymentCaptured(Event):
    pass

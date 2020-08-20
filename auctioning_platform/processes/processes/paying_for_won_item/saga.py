from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional
import uuid

from foundation.method_dispatch import method_dispatch
from foundation.value_objects import Money

from auctions import AuctionEnded
from customer_relationship import CustomerRelationshipFacade
from payments import PaymentCaptured, PaymentsFacade


class State(Enum):
    PAYMENT_STARTED = "PAYMENT_STARTED"
    TIMED_OUT = "TIMED_OUT"
    FINISHED = "FINISHED"


@dataclass
class PayingForWonItemData:
    process_uuid: uuid.UUID
    state: Optional[State] = None
    timeout_at: Optional[datetime] = None
    winning_bid: Optional[Money] = None
    auction_title: Optional[str] = None
    auction_id: Optional[int] = None
    winner_id: Optional[int] = None


class PayingForWonItem:
    def __init__(self, payments: PaymentsFacade, customer_relationship: CustomerRelationshipFacade) -> None:
        self._payments = payments
        self._customer_relationship = customer_relationship

    def timeout(self, data: PayingForWonItemData) -> None:
        assert data.timeout_at is not None and datetime.now() >= data.timeout_at
        assert data.state == State.PAYMENT_STARTED
        data.state = State.TIMED_OUT

    @method_dispatch
    def handle(self, event: Any, data: PayingForWonItemData) -> None:
        raise Exception(f"Unhandled event {event}")

    @handle.register(AuctionEnded)
    def handle_auction_ended(self, event: AuctionEnded, data: PayingForWonItemData) -> None:
        assert data.state is None
        payment_uuid = uuid.uuid4()
        self._payments.start_new_payment(payment_uuid, event.winner_id, event.winning_bid, event.auction_title)
        self._customer_relationship.send_email_about_winning(event.winner_id, event.winning_bid, event.auction_title)

        data.state = State.PAYMENT_STARTED
        data.auction_title = event.auction_title
        data.winning_bid = event.winning_bid
        data.timeout_at = datetime.now() + timedelta(days=3)
        data.auction_id = event.auction_id
        data.winner_id = event.winner_id

    @handle.register(PaymentCaptured)
    def handle_payment_captured(self, event: PaymentCaptured, data: PayingForWonItemData) -> None:
        assert data.state == State.PAYMENT_STARTED
        self._customer_relationship.send_email_after_successful_payment(
            event.customer_id, data.winning_bid, data.auction_title
        )

        data.state = State.FINISHED
        data.timeout_at = None

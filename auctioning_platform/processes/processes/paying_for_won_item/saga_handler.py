import uuid

import injector

from foundation.events import Event
from foundation.locks import LockFactory
from foundation.method_dispatch import method_dispatch

from auctions import AuctionEnded
from payments import PaymentCaptured
from processes.paying_for_won_item import PayingForWonItem, PayingForWonItemData
from processes.repository import ProcessManagerDataRepo


class PayingForWonItemHandler:
    LOCK_TIMEOUT = 30

    @injector.inject
    def __init__(
        self, process_manager: PayingForWonItem, repo: ProcessManagerDataRepo, lock_factory: LockFactory
    ) -> None:
        self._process_manager = process_manager
        self._repo = repo
        self._lock_factory = lock_factory

    @method_dispatch
    def __call__(self, event: Event) -> None:
        raise NotImplementedError

    @__call__.register(PaymentCaptured)
    def handle_payment_captured(self, event: PaymentCaptured) -> None:
        data = self._repo.get(event.payment_uuid, PayingForWonItemData)
        lock_name = f"pm-lock-{data.auction_id}-{data.winner_id}"
        self._run_process_manager(lock_name, data, event)

    @__call__.register(AuctionEnded)
    def handle_beginning(self, event: AuctionEnded) -> None:
        data = PayingForWonItemData(process_uuid=uuid.uuid4())
        lock_name = f"pm-lock-{event.auction_id}-{event.winner_id}"
        self._run_process_manager(lock_name, data, event)

    def _run_process_manager(self, lock_name: str, data: PayingForWonItemData, event: Event) -> None:
        lock = self._lock_factory(lock_name, self.LOCK_TIMEOUT)

        with lock:
            self._process_manager.handle(event, data)
            self._repo.save(data.process_uuid, data)

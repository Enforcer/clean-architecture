import uuid

import injector

from foundation.events import Event
from foundation.locks import LockFactory
from foundation.method_dispatch import method_dispatch

from auctions import AuctionEnded
from payments import PaymentCaptured

from processes.paying_for_won_item import PayingForWonItemSaga, PayingForWonItemSagaData
from processes.repository import SagaDataRepo


class PayingForWonItemSagaHandler:
    LOCK_TIMEOUT = 30

    @injector.inject
    def __init__(self, saga: PayingForWonItemSaga, repo: SagaDataRepo, lock_factory: LockFactory) -> None:
        self._saga = saga
        self._repo = repo
        self._lock_factory = lock_factory

    @method_dispatch
    def __call__(self, event: Event) -> None:
        raise NotImplementedError

    @__call__.register(PaymentCaptured)
    def handle_payment_captured(self, event: PaymentCaptured) -> None:
        data = self._repo.get(event.payment_uuid, PayingForWonItemSagaData)
        lock_name = f"saga-lock-{data.auction_id}-{data.winner_id}"
        self._run_saga(lock_name, data, event)

    @__call__.register(AuctionEnded)
    def handle_beginning(self, event: AuctionEnded) -> None:
        data = PayingForWonItemSagaData(saga_uuid=uuid.uuid4())
        lock_name = f'saga-lock-{getattr(event, "auction_id")}-{getattr(event, "winner_id")}'
        self._run_saga(lock_name, data, event)

    def _run_saga(self, lock_name: str, data: PayingForWonItemSagaData, event: Event) -> None:
        lock = self._lock_factory(lock_name, self.LOCK_TIMEOUT)

        with lock:
            self._saga.handle(event, data)
            self._repo.save(data.saga_uuid, data)

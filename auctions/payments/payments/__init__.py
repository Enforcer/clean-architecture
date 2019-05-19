import injector
from pybuses import EventBus
from sqlalchemy.engine import Connection

from payments.config import PaymentsConfig
from payments.events import PaymentCaptured, PaymentCharged, PaymentFailed, PaymentStarted
from payments.facade import PaymentsFacade

__all__ = ["PaymentsFacade", "PaymentsConfig", "PaymentStarted", "PaymentCharged", "PaymentCaptured", "PaymentFailed"]


EventsSubscriptions = injector.Key("payments_events_subscriptions")


class Payments(injector.Module):
    @injector.provider
    def facade(
        self,
        config: PaymentsConfig,
        connection: Connection,
        event_bus: EventBus,
        _subscriptions: EventsSubscriptions,  # type: ignore
    ) -> PaymentsFacade:
        return PaymentsFacade(config, connection, event_bus)

    @injector.singleton
    @injector.provider
    def subscribe_for_events(self, event_bus: EventBus) -> EventsSubscriptions:  # type: ignore
        event_bus.subscribe(run_charge_in_background)
        return  # type: ignore


def run_charge_in_background(event: PaymentCharged) -> None:
    # TODO: just extract parameters from `event` and call task
    pass

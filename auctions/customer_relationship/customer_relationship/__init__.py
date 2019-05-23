import injector
from sqlalchemy.engine import Connection

from foundation.events import ClassProviderMulti, Enqueue, Handler

from auctions.domain.events import BidderHasBeenOverbid, WinningBidPlaced

from customer_relationship.config import CustomerRelationshipConfig
from customer_relationship.facade import CustomerRelationshipFacade

__all__ = ["CustomerRelationship", "CustomerRelationshipConfig", "CustomerRelationshipFacade"]


class CustomerRelationship(injector.Module):
    @injector.provider
    def facade(
        self, config: CustomerRelationshipConfig, enqueue_fun: Enqueue, connection: Connection
    ) -> CustomerRelationshipFacade:
        return CustomerRelationshipFacade(config, enqueue_fun, connection)

    def configure(self, binder: injector.Binder) -> None:
        binder.multibind(Handler[BidderHasBeenOverbid], to=ClassProviderMulti(BidderHasBeenOverbidHandler))
        binder.multibind(Handler[WinningBidPlaced], to=ClassProviderMulti(WinningBidPlacedHandler))


class BidderHasBeenOverbidHandler:
    @injector.inject
    def __init__(self, facade: CustomerRelationshipFacade) -> None:
        self._facade = facade

    def __call__(self, event: BidderHasBeenOverbid) -> None:
        self._facade.send_email_about_overbid(event)


class WinningBidPlacedHandler:
    @injector.inject
    def __init__(self, facade: CustomerRelationshipFacade) -> None:
        self._facade = facade

    def __call__(self, event: WinningBidPlaced) -> None:
        self._facade.send_email_about_winning(event)

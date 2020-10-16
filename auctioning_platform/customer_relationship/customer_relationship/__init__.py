import injector
from sqlalchemy.engine import Connection

from foundation.events import AsyncEventHandlerProvider, AsyncHandler

from auctions import BidderHasBeenOverbid, WinningBidPlaced
from customer_relationship.config import CustomerRelationshipConfig
from customer_relationship.facade import CustomerRelationshipFacade
from customer_relationship.models import customers

__all__ = [
    # module
    "CustomerRelationship",
    "CustomerRelationshipConfig",
    # facade
    "CustomerRelationshipFacade",
    # models
    "customers",
]


class CustomerRelationship(injector.Module):
    @injector.provider
    def facade(self, config: CustomerRelationshipConfig, connection: Connection) -> CustomerRelationshipFacade:
        return CustomerRelationshipFacade(config, connection)

    def configure(self, binder: injector.Binder) -> None:
        binder.multibind(AsyncHandler[BidderHasBeenOverbid], to=AsyncEventHandlerProvider(BidderHasBeenOverbidHandler))
        binder.multibind(AsyncHandler[WinningBidPlaced], to=AsyncEventHandlerProvider(WinningBidPlacedHandler))


class BidderHasBeenOverbidHandler:
    @injector.inject
    def __init__(self, facade: CustomerRelationshipFacade) -> None:
        self._facade = facade

    def __call__(self, event: BidderHasBeenOverbid) -> None:
        self._facade.send_email_about_overbid(event.bidder_id, event.new_price, event.auction_title)


class WinningBidPlacedHandler:
    @injector.inject
    def __init__(self, facade: CustomerRelationshipFacade) -> None:
        self._facade = facade

    def __call__(self, event: WinningBidPlaced) -> None:
        self._facade.send_email_about_winning(event.bidder_id, event.bid_amount, event.auction_title)

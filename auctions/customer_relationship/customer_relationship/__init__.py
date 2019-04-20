import inject
from pybuses import EventBus

from auctions.application.queries import GetSingleAuction
from auctions.domain.events import BidderHasBeenOverbid, WinningBidPlaced
from customer_relationship import messages
from customer_relationship.email_sender import EmailSender
from customer_relationship.config import CustomerRelationshipConfig


class CustomerRelationshipFacade:
    def __init__(self, config: CustomerRelationshipConfig, event_bus: EventBus) -> None:
        self._sender = EmailSender(config)

        # event_bus.subscribe(self.send_email_about_overbid)
        # event_bus.subscribe(self.send_email_about_winning)

    def send_email_about_overbid(self, event: BidderHasBeenOverbid) -> None:
        auction_dto = inject.instance(GetSingleAuction).query(event.auction_id)
        message = messages.Overbid(auction_title=auction_dto.title, new_price=event.new_price)
        # TODO: create query OR sync data between contexts in different way
        self._sender.send("sebastian@cleanarchitecture.io", message)

    def send_email_about_winning(self, event: WinningBidPlaced) -> None:
        auction_dto = inject.instance(GetSingleAuction).query(event.auction_id)
        message = messages.Winning(auction_title=auction_dto.title, amount=event.bid_amount)
        self._sender.send("sebastian@cleanarchitecture.io", message)

from pybuses import EventBus

from auctions.domain.events import BidderHasBeenOverbid, WinningBidPlaced
from customer_relationship import emails
from customer_relationship.email_sender import EmailSender
from customer_relationship.config import CustomerRelationshipConfig


class CustomerRelationshipFacade:
    def __init__(self, config: CustomerRelationshipConfig, event_bus: EventBus) -> None:
        self._sender = EmailSender(config)

        # event_bus.subscribe(self.send_email_about_overbid)
        # event_bus.subscribe(self.send_email_about_winning)

    def send_email_about_overbid(self, event: BidderHasBeenOverbid) -> None:
        message = emails.Overbid(auction_title=event.auction_title, new_price=event.new_price)
        # TODO: create query OR sync data between contexts in different way
        self._sender.send("sebastian@cleanarchitecture.io", message)

    def send_email_about_winning(self, event: WinningBidPlaced) -> None:
        message = emails.Winning(auction_title=event.auction_title, amount=event.bid_amount)
        self._sender.send("sebastian@cleanarchitecture.io", message)

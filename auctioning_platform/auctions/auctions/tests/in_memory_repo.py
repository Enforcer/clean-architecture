from typing import Dict

from foundation.events import EventBus

from auctions.application.repositories import AuctionsRepository
from auctions.domain.entities import Auction
from auctions.domain.value_objects import AuctionId


class InMemoryAuctionsRepo(AuctionsRepository):
    def __init__(self, event_bus: EventBus):
        """
        Initialize bus bus.

        Args:
            self: (todo): write your description
            event_bus: (str): write your description
        """
        self._event_bus = event_bus
        self._data: Dict[AuctionId, Auction] = {}

    def get(self, auction_id: AuctionId) -> Auction:
        """
        Gets a specific creator.

        Args:
            self: (todo): write your description
            auction_id: (str): write your description
        """
        return self._data[auction_id]

    def save(self, auction: Auction) -> None:
        """
        Save all events to save

        Args:
            self: (todo): write your description
            auction: (todo): write your description
        """
        for event in auction.domain_events:
            self._event_bus.post(event)
        auction.clear_events()
        self._data[auction.id] = auction

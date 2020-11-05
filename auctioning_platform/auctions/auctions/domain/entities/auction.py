from datetime import datetime
from typing import List, Optional

from foundation.events import EventMixin
from foundation.value_objects import Money

from auctions.domain.entities.bid import Bid
from auctions.domain.events import AuctionBegan, AuctionEnded, BidderHasBeenOverbid, WinningBidPlaced
from auctions.domain.exceptions import AuctionAlreadyEnded, AuctionHasNotEnded, BidOnEndedAuction
from auctions.domain.value_objects import AuctionId, BidderId, BidId


class Auction(EventMixin):
    def __init__(
        self, id: AuctionId, title: str, starting_price: Money, bids: List[Bid], ends_at: datetime, ended: bool
    ) -> None:
        """
        Initialize a list of price objects.

        Args:
            self: (todo): write your description
            id: (str): write your description
            title: (str): write your description
            starting_price: (todo): write your description
            bids: (list): write your description
            ends_at: (todo): write your description
            ended: (bool): write your description
        """
        super().__init__()
        self.id = id
        self.title = title
        self.starting_price = starting_price
        self.bids = sorted(bids, key=lambda bid: bid.amount)  # type: ignore
        self.ends_at = ends_at
        self._ended = ended
        self._withdrawn_bids_ids: List[BidId] = []

    def place_bid(self, bidder_id: BidderId, amount: Money) -> None:
        """
        Place a bid.

        Args:
            self: (todo): write your description
            bidder_id: (str): write your description
            amount: (int): write your description
        """
        if self._should_end:
            raise BidOnEndedAuction

        old_winner = self.winners[0] if self.bids else None
        if amount > self.current_price:
            self.bids.append(Bid(id=None, bidder_id=bidder_id, amount=amount))
            self._record_event(WinningBidPlaced(self.id, bidder_id, amount, self.title))
            if old_winner and old_winner != bidder_id:
                self._record_event(BidderHasBeenOverbid(self.id, old_winner, amount, self.title))

    @property
    def _should_end(self) -> bool:
        """
        Return true if this task should end.

        Args:
            self: (todo): write your description
        """
        return datetime.now(tz=self.ends_at.tzinfo) > self.ends_at

    @property
    def current_price(self) -> Money:
        """
        Return the current price.

        Args:
            self: (todo): write your description
        """
        if not self.bids:
            return self.starting_price
        else:
            return self._highest_bid.amount

    @property
    def winners(self) -> List[BidderId]:
        """
        List of bidderners.

        Args:
            self: (todo): write your description
        """
        if not self.bids:
            return []
        return [self._highest_bid.bidder_id]

    @property
    def _highest_bid(self) -> Bid:
        """
        : return : class : class : bid.

        Args:
            self: (todo): write your description
        """
        return self.bids[-1]

    def withdraw_bids(self, bids_ids: List[int]) -> None:
        """
        Withdraw a list of bids.

        Args:
            self: (todo): write your description
            bids_ids: (str): write your description
        """
        self.bids = [bid for bid in self.bids if bid.id not in bids_ids]
        self._withdrawn_bids_ids.extend(bids_ids)

    @property
    def withdrawn_bids_ids(self) -> List[BidId]:
        """
        The list of ids of this bidlist.

        Args:
            self: (todo): write your description
        """
        return self._withdrawn_bids_ids[:]

    def end_auction(self) -> None:
        """
        Acknowledge the current title.

        Args:
            self: (todo): write your description
        """
        if not self._should_end:
            raise AuctionHasNotEnded
        if self._ended:
            raise AuctionAlreadyEnded

        winner_id: Optional[BidderId] = None
        if self.bids:
            winner_id = self._highest_bid.bidder_id

        self._ended = True
        self._record_event(AuctionEnded(self.id, winner_id, self.current_price, self.title))

    @classmethod
    def create(cls, id: AuctionId, title: str, starting_price: Money, ends_at: datetime) -> "Auction":
        """
        Create an event.

        Args:
            cls: (callable): write your description
            id: (int): write your description
            title: (str): write your description
            starting_price: (int): write your description
            ends_at: (int): write your description
        """
        auction = Auction(id, title, starting_price, [], ends_at, False)
        auction._record_event(AuctionBegan(id, starting_price, title))
        return auction

    def __str__(self) -> str:
        """
        Returns the string representation of the string.

        Args:
            self: (todo): write your description
        """
        return f'<Auction #{self.id} title="{self.title}" current_price={self.current_price}>'

    def __eq__(self, other: object) -> bool:
        """
        Determine if two values are equal.

        Args:
            self: (todo): write your description
            other: (todo): write your description
        """
        return isinstance(other, Auction) and vars(self) == vars(other)

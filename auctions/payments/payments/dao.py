from auctions.domain.types import AuctionId, BidderId
from auctions.domain.value_objects import Money


def get_bidders_card_token(bidder_id: BidderId) -> str:
    raise NotImplementedError


def record_successful_payment(auction_id: AuctionId, bidder_id: BidderId, charge: Money, charge_uuid: str) -> None:
    raise NotImplementedError

from auctions.domain.types import (
    AuctionId,
    BidderId,
)
from auctions.domain.value_objects import Money
from auctions_infrastructure.models import (
    BidderCardDetails,
    PaymentHistoryEntry,
)


def get_bidders_card_token(bidder_id: BidderId) -> str:
    card_details_model = BidderCardDetails.objects.filter(bidder_id=bidder_id).first()
    return card_details_model.card_token


def record_successful_payment(auction_id: AuctionId, bidder_id: BidderId, charge: Money, charge_uuid: str) -> None:
    PaymentHistoryEntry.objects.create(
        auction_id=auction_id,
        bidder_id=bidder_id,
        amount=charge.amount,
        currency=charge.currency.iso_code,
        charge_uuid=charge_uuid
    )

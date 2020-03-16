import injector

from auctions.application.queries import GetActiveAuctions, GetSingleAuction
from auctions.application.repositories import AuctionsRepository
from auctions.application.use_cases import (
    BeginningAuction,
    BeginningAuctionInputDto,
    EndingAuction,
    EndingAuctionInputDto,
    PlacingBid,
    PlacingBidInputDto,
    PlacingBidOutputBoundary,
    WithdrawingBids,
    WithdrawingBidsInputDto,
)
from auctions.domain.events import AuctionBegan, AuctionEnded, BidderHasBeenOverbid, WinningBidPlaced

__all__ = [
    # module
    "Auctions",
    # events
    "AuctionBegan",
    "AuctionEnded",
    "WinningBidPlaced",
    "BidderHasBeenOverbid",
    # repositories
    "AuctionsRepository",
    # use cases
    "PlacingBid",
    "PlacingBidOutputBoundary",
    "WithdrawingBids",
    # input dtos
    "BeginningAuctionInputDto",
    "EndingAuctionInputDto",
    "PlacingBidInputDto",
    "WithdrawingBidsInputDto",
    # queries
    "GetActiveAuctions",
    "GetSingleAuction",
]


class Auctions(injector.Module):
    @injector.provider
    def placing_bid_uc(self, boundary: PlacingBidOutputBoundary, repo: AuctionsRepository) -> PlacingBid:
        return PlacingBid(boundary, repo)

    @injector.provider
    def withdrawing_bids_uc(self, repo: AuctionsRepository) -> WithdrawingBids:
        return WithdrawingBids(repo)

    @injector.provider
    def ending_auction_uc(self, repo: AuctionsRepository) -> EndingAuction:
        return EndingAuction(repo)

    @injector.provider
    def beginning_auction_uc(self, repo: AuctionsRepository) -> BeginningAuction:
        return BeginningAuction(repo)

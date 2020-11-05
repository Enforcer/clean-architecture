from flask import Blueprint, Response, abort, jsonify, make_response, request
import flask_injector
from flask_login import current_user
import injector

from auctions import (
    AuctionId,
    GetActiveAuctions,
    GetSingleAuction,
    PlacingBid,
    PlacingBidInputDto,
    PlacingBidOutputBoundary,
    PlacingBidOutputDto,
)
from web_app.serialization.dto import get_dto

auctions_blueprint = Blueprint("auctions_blueprint", __name__)


class AuctionsWeb(injector.Module):
    @injector.provider
    @flask_injector.request
    def placing_bid_output_boundary(self) -> PlacingBidOutputBoundary:
        """
        Returns the output of the convolutionalid.

        Args:
            self: (todo): write your description
        """
        return PlacingBidPresenter()


@auctions_blueprint.route("/")
def auctions_list(query: GetActiveAuctions) -> Response:
    """
    Gets a list of all active response.

    Args:
        query: (str): write your description
    """
    return make_response(jsonify(query.query()))


@auctions_blueprint.route("/<int:auction_id>")
def single_auction(auction_id: int, query: GetSingleAuction) -> Response:
    """
    Makes a response.

    Args:
        auction_id: (str): write your description
        query: (str): write your description
    """
    return make_response(jsonify(query.query(auction_id)))


@auctions_blueprint.route("/<int:auction_id>/bids", methods=["POST"])
def place_bid(auction_id: AuctionId, placing_bid_uc: PlacingBid, presenter: PlacingBidOutputBoundary) -> Response:
    """
    Place a flight_authenticated.

    Args:
        auction_id: (str): write your description
        placing_bid_uc: (todo): write your description
        presenter: (todo): write your description
    """
    if not current_user.is_authenticated:
        abort(403)

    dto = get_dto(request, PlacingBidInputDto, context={"auction_id": auction_id, "bidder_id": current_user.id})

    placing_bid_uc.execute(dto)
    return presenter.response  # type: ignore


class PlacingBidPresenter(PlacingBidOutputBoundary):
    response: Response

    def present(self, output_dto: PlacingBidOutputDto) -> None:
        """
        Ensure that the output is present response.

        Args:
            self: (todo): write your description
            output_dto: (array): write your description
        """
        message = (
            "Hooray! You are a winner"
            if output_dto.is_winner
            else f"Your bid is too low. Current price is {output_dto.current_price}"
        )
        self.response = make_response(jsonify({"message": message}))

from typing import Type

from flask import Blueprint, Response, abort, jsonify, make_response, request
from flask_login import current_user
import injector
from marshmallow import Schema, exceptions as marshmallow_exceptions, fields, post_load

from foundation.value_objects.factories import get_dollars

from auctions.application import queries as auction_queries
from auctions.application.use_cases import placing_bid
from auctions.domain.types import AuctionId

auctions_blueprint = Blueprint("auctions_blueprint", __name__)


class AuctionsWeb(injector.Module):
    @injector.provider
    def placing_bid_output_boundary(self) -> placing_bid.PlacingBidOutputBoundary:
        return PlacingBidPresenter()


class Dollars(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        return str(value)

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return get_dollars(value)
        except ValueError as exc:
            raise marshmallow_exceptions.ValidationError(str(exc))


def get_input_dto(schema_cls: Type[Schema], context: dict) -> placing_bid.PlacingBidInputDto:
    schema = schema_cls(context=context)
    try:
        return schema.load(request.json)
    except marshmallow_exceptions.ValidationError as exc:
        abort(make_response(jsonify(exc.messages), 400))


class PlacingBidSchema(Schema):
    amount = Dollars()

    @post_load
    def make_dto(self, data: dict):
        return placing_bid.PlacingBidInputDto(**self.context, **data)


class PlacingBidPresenter(placing_bid.PlacingBidOutputBoundary):
    response: Response

    def present(self, output_dto: placing_bid.PlacingBidOutputDto) -> None:
        message = (
            f"Hooray! You are a winner"
            if output_dto.is_winner
            else f"Your bid is too low. Current price is {output_dto.current_price}"
        )
        self.response = make_response(jsonify({"message": message}))


@auctions_blueprint.route("/")
def auctions_list(query: auction_queries.GetActiveAuctions) -> Response:
    return make_response(jsonify(query.query()))


@auctions_blueprint.route("/<int:auction_id>")
def single_auction(auction_id: int, query: auction_queries.GetSingleAuction) -> Response:
    return make_response(jsonify(query.query(auction_id)))


@auctions_blueprint.route("/<int:auction_id>/bids", methods=["POST"])
def place_bid(auction_id: AuctionId, placing_bid_uc: placing_bid.PlacingBid) -> Response:
    if not current_user.is_authenticated:
        abort(403)

    placing_bid_uc.execute(
        get_input_dto(PlacingBidSchema, context={"auction_id": auction_id, "bidder_id": current_user.id})
    )
    return placing_bid_uc.output_boundary.response

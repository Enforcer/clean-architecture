from typing import Type

from flask import Blueprint, Response, abort, jsonify, make_response, request
import flask_injector
from flask_login import current_user
import injector
from marshmallow import Schema, exceptions as marshmallow_exceptions, fields, post_load

from foundation.value_objects.factories import get_dollars

from auctions import (
    AuctionId,
    GetActiveAuctions,
    GetSingleAuction,
    PlacingBid,
    PlacingBidInputDto,
    PlacingBidOutputBoundary,
    PlacingBidOutputDto,
)

auctions_blueprint = Blueprint("auctions_blueprint", __name__)


class AuctionsWeb(injector.Module):
    @injector.provider
    @flask_injector.request
    def placing_bid_output_boundary(self) -> PlacingBidOutputBoundary:
        return PlacingBidPresenter()


class Dollars(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):  # type: ignore
        return str(value)

    def _deserialize(self, value, attr, data, **kwargs):  # type: ignore
        try:
            return get_dollars(value)
        except ValueError as exc:
            raise marshmallow_exceptions.ValidationError(str(exc))


def get_input_dto(schema_cls: Type[Schema], context: dict) -> PlacingBidInputDto:
    schema = schema_cls(context=context)
    try:
        return schema.load(request.json)
    except marshmallow_exceptions.ValidationError as exc:
        abort(make_response(jsonify(exc.messages), 400))


class PlacingBidSchema(Schema):
    amount = Dollars()

    @post_load
    def make_dto(self, data: dict, **_kwargs: dict) -> PlacingBidInputDto:
        return PlacingBidInputDto(**self.context, **data)


class PlacingBidPresenter(PlacingBidOutputBoundary):
    response: Response

    def present(self, output_dto: PlacingBidOutputDto) -> None:
        message = (
            f"Hooray! You are a winner"
            if output_dto.is_winner
            else f"Your bid is too low. Current price is {output_dto.current_price}"
        )
        self.response = make_response(jsonify({"message": message}))


@auctions_blueprint.route("/")
def auctions_list(query: GetActiveAuctions) -> Response:
    return make_response(jsonify(query.query()))  # type: ignore


@auctions_blueprint.route("/<int:auction_id>")
def single_auction(auction_id: int, query: GetSingleAuction) -> Response:
    return make_response(jsonify(query.query(auction_id)))  # type: ignore


@auctions_blueprint.route("/<int:auction_id>/bids", methods=["POST"])
def place_bid(auction_id: AuctionId, placing_bid_uc: PlacingBid, presenter: PlacingBidOutputBoundary) -> Response:
    if not current_user.is_authenticated:
        abort(403)

    placing_bid_uc.execute(
        get_input_dto(PlacingBidSchema, context={"auction_id": auction_id, "bidder_id": current_user.id})
    )
    return presenter.response  # type: ignore

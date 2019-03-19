from typing import Type

import inject
from flask import Blueprint, abort, jsonify, make_response, request, Response
from marshmallow import fields, exceptions as marshmallow_exceptions, post_load, Schema


from auctions.application.use_cases import placing_bid
from auctions.application import queries as auction_queries
from auctions.domain.factories import get_dollars
from auctions.domain.types import AuctionId


auctions_blueprint = Blueprint("auctions_blueprint", __name__)


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
    def __init__(self) -> None:
        self.response = None

    def present(self, output_dto: placing_bid.PlacingBidOutputDto) -> None:
        message = (
            f"Hooray! You are a winner"
            if output_dto.is_winner
            else f"Your bid is too low. Current price is {output_dto.current_price}"
        )
        self.response = make_response(jsonify({"message": message}))


@auctions_blueprint.route("/")
@inject.autoparams("query")
def auctions_list(query: auction_queries.GetActiveAuctions) -> Response:
    return make_response(jsonify(query.query()))


@auctions_blueprint.route("/<int:auction_id>")
@inject.autoparams("query")
def single_auction(auction_id: int, query: auction_queries.GetSingleAuction) -> Response:
    return make_response(jsonify(query.query(auction_id)))


@auctions_blueprint.route("/<int:auction_id>/bids", methods=["POST"])
def place_bid(auction_id: AuctionId) -> Response:
    presenter = PlacingBidPresenter()

    placing_bid.PlacingBid(output_boundary=presenter).execute(
        get_input_dto(
            PlacingBidSchema,
            context={
                "auction_id": auction_id,
                "bidder_id": 2,  # hardcoded for now, should be taken from request authentication
            },
        )
    )

    return presenter.response

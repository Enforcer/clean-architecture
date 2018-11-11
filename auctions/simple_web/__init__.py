from typing import Type

from flask import (
    Flask,
    abort,
    jsonify,
    make_response,
    request,
)
from marshmallow import (
    fields,
    exceptions as marshmallow_exceptions,
    post_load,
    Schema,
)

from .main import setup


from auctions.application.use_cases import placing_bid
from auctions.domain.types import AuctionId
from auctions.domain.factories import get_dollars


app = Flask(__name__)
setup()


@app.before_request
def only_json():
    if not request.is_json:
        abort(400)


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
            f'Hooray! You are a winner'
            if output_dto.is_winner
            else f'Your bid is too low. Current price is {output_dto.current_price}'
        )
        self.response = make_response(jsonify({'message': message}))


@app.route('/<int:auction_id>/bid', methods=['POST'])
def place_bid(auction_id: AuctionId) -> app.response_class:
    presenter = PlacingBidPresenter()

    placing_bid.PlacingBid(
        output_boundary=presenter
    ).execute(
        get_input_dto(PlacingBidSchema, context={
            'auction_id': auction_id,
            'bidder_id': 1,  # hardcoded for now, should be taken from request authentication
        })
    )

    return presenter.response

from datetime import datetime
from typing import Type

import inject
from flask import (
    Flask,
    abort,
    jsonify,
    make_response,
    request,
    json,
)
from marshmallow import (
    fields,
    exceptions as marshmallow_exceptions,
    post_load,
    Schema,
)

from .main import setup


from auctions.application.use_cases import placing_bid
from auctions.application.repositories import AuctionsRepository
from auctions.domain.entities import Auction
from auctions.domain.factories import get_dollars
from auctions.domain.types import AuctionId
from auctions.domain.value_objects import Money
from foundation.method_dispatch import method_dispatch


class JSONEncoder(json.JSONEncoder):
    @method_dispatch
    def default(self, obj: object) -> object:
        raise TypeError(f'Cannot serialize {type(obj)}')

    @default.register(Auction)
    def _(self, obj: Auction) -> object:
        return {
            'id': obj.id,
            'title': obj.title,
            'current_price': obj.current_price,
            'starting_price': obj.starting_price,
            'ends_at': obj.ends_at,
        }

    @default.register(Money)
    def _(self, obj: Money) -> object:
        return {
            'amount': str(obj.amount),
            'currency': obj.currency.iso_code,
        }

    @default.register(datetime)
    def _(self, obj: datetime) -> str:
        return obj.isoformat()


app = Flask(__name__)
app.json_encoder = JSONEncoder
setup(app)


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


@app.route('/')
def auctions_list() -> app.response_class:
    inst = inject.instance(AuctionsRepository)

    return make_response(jsonify([inst.get_active()]))


@app.route('/<int:auction_id>')
def single_auction(auction_id: int) -> app.response_class:
    inst = inject.instance(AuctionsRepository)

    auction = inst.get(auction_id)
    return make_response(jsonify(auction))


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

from datetime import datetime

from flask import Flask, json, abort, request

from .main import setup
from .blueprints.auctions import auctions_blueprint
from auctions.application import queries as auction_queries
from auctions.domain.value_objects import Money
from foundation.method_dispatch import method_dispatch


class JSONEncoder(json.JSONEncoder):
    @method_dispatch
    def default(self, obj: object) -> object:
        raise TypeError(f"Cannot serialize {type(obj)}")

    @default.register(auction_queries.AuctionDto)  # noqa: F811
    def _(self, obj: auction_queries.AuctionDto) -> object:
        return {
            "id": obj.id,
            "title": obj.title,
            "current_price": obj.current_price,
            "starting_price": obj.starting_price,
            "ends_at": obj.ends_at,
        }

    @default.register(Money)  # noqa: F811
    def _(self, obj: Money) -> object:
        return {"amount": str(obj.amount), "currency": obj.currency.iso_code}

    @default.register(datetime)  # noqa: F811
    def _(self, obj: datetime) -> str:
        return obj.isoformat()


def create_app() -> Flask:
    app = Flask(__name__)

    app.json_encoder = JSONEncoder

    @app.before_request
    def only_json():
        if not request.is_json:
            abort(400)

    app.register_blueprint(auctions_blueprint)

    setup(app)

    return app

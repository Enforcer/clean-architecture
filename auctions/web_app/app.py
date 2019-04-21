from datetime import datetime

from flask import Flask, json, abort, request

from .main import setup
from .blueprints.auctions import auctions_blueprint
from .security import setup as security_setup
from auctions.application import queries as auction_queries
from auctions.domain.value_objects import Money
from foundation.method_dispatch import method_dispatch


class JSONEncoder(json.JSONEncoder):
    @method_dispatch
    def default(self, obj: object) -> object:
        raise TypeError(f"Cannot serialize {type(obj)}")

    @default.register(auction_queries.AuctionDto)  # noqa: F811
    def serialize_auction_dto(self, obj: auction_queries.AuctionDto) -> object:
        return {
            "id": obj.id,
            "title": obj.title,
            "current_price": obj.current_price,
            "starting_price": obj.starting_price,
            "ends_at": obj.ends_at,
        }

    @default.register(Money)  # noqa: F811
    def serialize_money(self, obj: Money) -> object:
        return {"amount": str(obj.amount), "currency": obj.currency.iso_code}

    @default.register(datetime)  # noqa: F811
    def serialize_datetime(self, obj: datetime) -> str:
        return obj.isoformat()


def create_app() -> Flask:
    app = Flask(__name__)

    app.json_encoder = JSONEncoder

    @app.before_request
    def only_json():
        if not request.is_json:
            abort(400)

    app.register_blueprint(auctions_blueprint)

    # TODO: move this config
    app.config["SECRET_KEY"] = "super-secret"
    app.config["DEBUG"] = True
    app.config["SECURITY_SEND_REGISTER_EMAIL"] = False
    app.config["SECURITY_REGISTERABLE"] = True
    app.config["SECURITY_PASSWORD_SALT"] = "99f885320c0f867cde17876a7849904c41a2b8120a9a9e76d1789e458e543af9"
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["DB_DSN"] = "sqlite:///foo.db"

    setup(app)
    security_setup(app)

    return app

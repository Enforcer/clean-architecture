from datetime import datetime

from flask import Flask, Response, json, request
from flask_injector import FlaskInjector
from main import bootstrap_app

from foundation.method_dispatch import method_dispatch
from foundation.value_objects import Money

from auctions import AuctionDto
from web_app.blueprints.auctions import AuctionsWeb, auctions_blueprint
from web_app.blueprints.shipping import shipping_blueprint
from web_app.security import setup as security_setup


class JSONEncoder(json.JSONEncoder):
    @method_dispatch
    def default(self, obj: object) -> object:
        raise TypeError(f"Cannot serialize {type(obj)}")

    @default.register(AuctionDto)  # noqa: F811
    def serialize_auction_dto(self, obj: AuctionDto) -> object:
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

    app.register_blueprint(auctions_blueprint, url_prefix="/auctions")
    app.register_blueprint(shipping_blueprint, url_prefix="/shipping")

    # TODO: move this config
    app.config["SECRET_KEY"] = "super-secret"
    app.config["DEBUG"] = True
    app.config["SECURITY_SEND_REGISTER_EMAIL"] = False
    app.config["SECURITY_REGISTERABLE"] = True
    app.config["SECURITY_PASSWORD_SALT"] = "99f885320c0f867cde17876a7849904c41a2b8120a9a9e76d1789e458e543af9"
    app.config["WTF_CSRF_ENABLED"] = False

    app_context = bootstrap_app()
    FlaskInjector(app, modules=[AuctionsWeb()], injector=app_context.injector)

    @app.before_request
    def transaction_start() -> None:
        request.tx = app_context.connection_provider.open().begin()
        request.session = app_context.connection_provider.provide_session()

    @app.after_request
    def transaction_commit(response: Response) -> Response:
        try:
            if hasattr(request, "tx") and response.status_code < 400:
                request.tx.commit()
        finally:
            app_context.connection_provider.close_if_present()

        return response

    @app.after_request
    def add_cors_headers(response: Response) -> Response:
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response

    # has to be after DB-hooks, because it relies on DB
    security_setup(app)

    return app

from dataclasses import dataclass
import os

import dotenv
import injector
from sqlalchemy import event as sa_event
from sqlalchemy.engine import Connection, Engine, create_engine

from auctions import Auctions
from auctions_infrastructure import AuctionsInfrastructure
from customer_relationship import CustomerRelationship, CustomerRelationshipFacade
from db_infrastructure import metadata
from payments import Payments
from processes import Processes
from shipping import Shipping
from shipping_infrastructure import ShippingInfrastructure
from web_app_models import User

from main.db import ThreadlocalConnectionProvider
from main.modules import Configs, Db, EventBusMod, RedisMod, Rq

__all__ = ["bootstrap_app"]


@dataclass
class App:
    connection_provider: ThreadlocalConnectionProvider
    injector: injector.Injector


def bootstrap_app() -> App:
    """This is bootstrap function independent from the context.

    This should be used for Web, CLI, or worker context."""
    config_path = os.environ.get(
        "CONFIG_PATH", os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, ".env_file")
    )
    dotenv.load_dotenv(config_path)
    settings = {
        "payments.login": os.environ["PAYMENTS_LOGIN"],
        "payments.password": os.environ["PAYMENTS_PASSWORD"],
        "email.host": os.environ["EMAIL_HOST"],
        "email.port": os.environ["EMAIL_PORT"],
        "email.username": os.environ["EMAIL_USERNAME"],
        "email.password": os.environ["EMAIL_PASSWORD"],
        "email.from.name": os.environ["EMAIL_FROM_NAME"],
        "email.from.address": os.environ["EMAIL_FROM_ADDRESS"],
        "redis.host": os.environ["REDIS_HOST"],
    }

    engine = create_engine(os.environ["DB_DSN"])
    connection_provider = ThreadlocalConnectionProvider(engine)
    dependency_injector = _setup_dependency_injection(settings, connection_provider)
    _setup_orm_events(dependency_injector)

    _create_db_schema(engine)  # TEMPORARY

    return App(connection_provider, dependency_injector)


def _setup_dependency_injection(
    settings: dict, connection_provider: ThreadlocalConnectionProvider
) -> injector.Injector:
    return injector.Injector(  # type: ignore
        [
            Db(connection_provider),
            RedisMod(settings["redis.host"]),
            Rq(),
            EventBusMod(),
            Configs(settings),
            Auctions(),
            AuctionsInfrastructure(),
            Shipping(),
            ShippingInfrastructure(),
            CustomerRelationship(),
            Payments(),
            Processes(),
        ],
        auto_bind=False,
    )


def _setup_orm_events(dependency_injector: injector.Injector) -> None:
    @sa_event.listens_for(User, "after_insert")
    def insert_cb(_mapper, _connection: Connection, user: User) -> None:  # type: ignore
        dependency_injector.get(CustomerRelationshipFacade).create_customer(user.id, user.email)

    @sa_event.listens_for(User, "after_update")
    def update_cb(_mapper, _connection: Connection, user: User) -> None:  # type: ignore
        dependency_injector.get(CustomerRelationshipFacade).update_customer(user.id, user.email)


def _create_db_schema(engine: Engine) -> None:
    # Models has to be imported for metadata.create_all to discover them
    from auctions_infrastructure import auctions, bids  # noqa
    from customer_relationship.models import customers  # noqa
    from web_app_models import Role, RolesUsers, User  # noqa

    # TODO: Use migrations for that
    metadata.create_all(engine)

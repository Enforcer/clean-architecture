import os

from _pytest.tmpdir import TempPathFactory
from flask import Flask, testing
import injector
import pytest
from sqlalchemy.engine import Connection, create_engine

from web_app.app import create_app


@pytest.fixture(scope="session")
def config_path(tmp_path_factory: TempPathFactory) -> str:
    temp_dir = tmp_path_factory.mktemp("config")
    db_dir = tmp_path_factory.mktemp("test_db")
    conf_file_path = temp_dir / ".test_env_file"
    with open(conf_file_path, "w") as f:
        f.writelines(
            [
                "PAYMENTS_LOGIN=empty\n",
                "PAYMENTS_PASSWORD=empty\n",
                "EMAIL_HOST=localhost\n",
                "EMAIL_PORT=2525\n",
                "EMAIL_USERNAME=none\n",
                "EMAIL_PASSWORD=none\n",
                "EMAIL_FROM_NAME=Auctions\n",
                "EMAIL_FROM_ADDRESS=auctions@cleanarchitecture.io\n",
                "REDIS_HOST=localhost\n",
                f"DB_DSN=sqlite:///{db_dir}/db.sqlite\n",
            ]
        )
    return str(conf_file_path)


@pytest.fixture(scope="session")
def app(config_path: str) -> Flask:
    os.environ["CONFIG_PATH"] = config_path
    # Disable password hashing in tests to get speed-up
    settings_to_override = {
        "SECURITY_PASSWORD_HASH": "plaintext",
        "SECURITY_HASHING_SCHEMES": ["hex_md5"],
        "SECURITY_DEPRECATED_HASHING_SCHEMES": [],
    }
    return create_app(settings_to_override)


@pytest.fixture()
def container(app: Flask) -> injector.Injector:
    return app.injector  # type: ignore


@pytest.fixture()
def client(app: Flask) -> testing.FlaskClient:
    return app.test_client()


@pytest.fixture()
def connection() -> Connection:
    engine = create_engine(os.environ["DB_DSN"])
    yield engine.connect()
    engine.dispose()

import threading

from sqlalchemy.engine import Connection, Engine
from sqlalchemy.orm import Session


class ThreadlocalConnectionProvider:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        self._storage = threading.local()

    def __call__(self) -> Connection:
        try:
            return self._storage.connection
        except AttributeError:
            raise Exception("No connection available")

    def provide_session(self) -> Session:
        if not self.connected:
            raise Exception("No connection available")

        return self._storage.session

    @property
    def connected(self) -> bool:
        return hasattr(self._storage, "connection")

    def open(self) -> Connection:
        assert not hasattr(self._storage, "connection")
        connection = self._engine.connect()
        self._storage.connection = connection
        self._storage.session = Session(bind=connection)
        return connection

    def close_if_present(self) -> None:
        try:
            self._storage.connection.close()
            del self._storage.connection
            del self._storage.session
        except AttributeError:
            pass

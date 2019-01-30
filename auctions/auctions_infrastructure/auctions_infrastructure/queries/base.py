import inject

from sqlalchemy.engine import Connection


class SqlQuery:
    @inject.autoparams("connection")
    def __init__(self, connection: Connection) -> None:
        self._conn = connection

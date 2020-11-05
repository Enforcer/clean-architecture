from sqlalchemy.engine import Connection


class SqlQuery:
    def __init__(self, connection: Connection) -> None:
        """
        Initialize a connection.

        Args:
            self: (todo): write your description
            connection: (todo): write your description
        """
        self._conn = connection

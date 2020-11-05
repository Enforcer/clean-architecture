import json
from typing import Type, TypeVar, cast
from uuid import UUID

from sqlalchemy import Column, Table, Text
from sqlalchemy.engine import Connection

from foundation import serializing

from db_infrastructure import GUID, metadata

T = TypeVar("T")


process_manager_data_table = Table(
    "process_manager_data", metadata, Column("uuid", GUID, primary_key=True), Column("json", Text, nullable=False)
)


class ProcessManagerDataRepo:
    def __init__(self, connection: Connection) -> None:
        """
        Initialize a connection.

        Args:
            self: (todo): write your description
            connection: (todo): write your description
        """
        self._connection = connection

    def get(self, process_uuid: UUID, data_cls: Type[T]) -> T:
        """
        Get a single document.

        Args:
            self: (todo): write your description
            process_uuid: (str): write your description
            data_cls: (todo): write your description
        """
        row = self._connection.execute(
            process_manager_data_table.select(process_manager_data_table.c.uuid == process_uuid)
        ).first()
        return cast(T, serializing.from_json(json.loads(row.json), data_cls))

    def save(self, process_uuid: UUID, data: T) -> None:
        """
        Save the given uuid in the db.

        Args:
            self: (todo): write your description
            process_uuid: (todo): write your description
            data: (array): write your description
        """
        data = serializing.to_json(data)
        row = self._connection.execute(
            process_manager_data_table.select(process_manager_data_table.c.uuid == process_uuid)
        ).first()
        if row:
            self._connection.execute(
                process_manager_data_table.update(values={"json": data}).where(
                    process_manager_data_table.c.uuid == process_uuid
                )
            )
        else:
            self._connection.execute(process_manager_data_table.insert(values={"uuid": process_uuid, "json": data}))

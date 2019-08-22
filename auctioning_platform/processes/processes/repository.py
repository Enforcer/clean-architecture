import json
from typing import Type, TypeVar, cast
from uuid import UUID

from sqlalchemy import Column, Table, Text
from sqlalchemy.engine import Connection

from foundation import serializing

from db_infrastructure import GUID, metadata

T = TypeVar("T")


saga_data_table = Table(
    "saga_data", metadata, Column("uuid", GUID, primary_key=True), Column("json", Text, nullable=False)
)


class SagaDataRepo:
    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def get(self, saga_data_uuid: UUID, saga_data_cls: Type[T]) -> T:
        row = self._connection.execute(saga_data_table.select(saga_data_table.c.uuid == saga_data_uuid)).first()
        return cast(T, serializing.from_json(json.loads(row.json), saga_data_cls))

    def save(self, saga_data_uuid: UUID, saga_data: T) -> None:
        data = serializing.to_json(saga_data)
        row = self._connection.execute(saga_data_table.select(saga_data_table.c.uuid == saga_data_uuid)).first()
        if row:
            self._connection.execute(
                saga_data_table.update(values={"json": data}).where(saga_data_table.c.uuid == saga_data_uuid)
            )
        else:
            self._connection.execute(saga_data_table.insert(values={"uuid": saga_data_uuid, "json": data}))

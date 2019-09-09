from sqlalchemy import Column, Enum, Integer, String, Table

from db_infrastructure import GUID, metadata
from shipping.domain.value_objects import PackageStatus

packages = Table(
    "packages",
    metadata,
    Column("uuid", GUID, primary_key=True),
    Column("item_identifier", String(255), nullable=False),
    Column("consignee_id", Integer, nullable=False),
    Column("street", String(40), nullable=False),
    Column("house_number", String(40), nullable=False),
    Column("city", String(40), nullable=False),
    Column("state", String(40), nullable=False),
    Column("zip_code", String(40), nullable=False),
    Column("country", String(40), nullable=False),
    Column("status", Enum(PackageStatus), nullable=False),
)

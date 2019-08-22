from sqlalchemy import Column, Integer, String, Table

from db_infrastructure import metadata

payments = Table(
    "payments",
    metadata,
    Column("uuid", String(32), primary_key=True),
    Column("customer_id", Integer, nullable=False),
    Column("amount", Integer, nullable=False),
    Column("currency", String(5), nullable=False),
    Column("description", String, nullable=False),
    Column("status", String(32), nullable=False),
    Column("charge_id", String(32), nullable=True),
)

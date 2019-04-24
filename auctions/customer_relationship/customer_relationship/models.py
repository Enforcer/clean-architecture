from sqlalchemy import Column, Integer, String, Table

from db_infrastructure import metadata

customers = Table(
    "customers", metadata, Column("id", Integer, primary_key=True), Column("email", String(255), unique=True)
)

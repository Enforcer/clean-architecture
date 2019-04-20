from sqlalchemy import Table, Column, Integer, String, Numeric, ForeignKey, DateTime

from db_infrastructure import Base


metadata = Base.metadata


bidders = Table("bidders", metadata, Column("id", Integer, primary_key=True), Column("email", String(255), unique=True))


auctions = Table(
    "auctions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(255), nullable=False),
    Column("starting_price", Numeric, nullable=False),
    Column("current_price", Numeric, nullable=False),
    Column("ends_at", DateTime, nullable=False),
)


bids = Table(
    "bids",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("amount", Numeric, nullable=False),
    Column("bidder_id", None, ForeignKey("bidders.id"), nullable=False),
    Column("auction_id", None, ForeignKey("auctions.id"), nullable=False),
)

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Table

from db_infrastructure import metadata

bidders = Table("bidders", metadata, Column("id", Integer, primary_key=True), Column("email", String(255), unique=True))


auctions = Table(
    "auctions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(255), nullable=False),
    Column("starting_price", Numeric, nullable=False),
    Column("current_price", Numeric, nullable=False),
    Column("ends_at", DateTime, nullable=False),
    Column("ended", Boolean, nullable=False, default=False),
)


bids = Table(
    "bids",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("amount", Numeric, nullable=False),
    Column("bidder_id", None, ForeignKey("bidders.id"), nullable=False),
    Column("auction_id", None, ForeignKey("auctions.id"), nullable=False),
)

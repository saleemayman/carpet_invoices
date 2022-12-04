from sqlalchemy import Column, Integer, String, DateTime, BIGINT, ForeignKey
from sqlalchemy.sql import func

from database.base import Base
from definitions.schemas import Schemas


class SourceMetaDataTable(Base):
    __tablename__ = "dim_raw_source_metadata"
    __table_args__ = {"schema": Schemas.RAW.value}

    source_id = Column(Integer, primary_key=True, unique=True)
    source_name = Column(String, nullable=False)
    source_type = Column(String, nullable=False)
    source_filename = Column(String)
    date_inserted = Column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False,
    )


class AmazonSalesTable(Base):
    __tablename__ = "amazon_sales_data"
    __table_args__ = {"schema": Schemas.RAW.value}

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    uid = Column(BIGINT)
    date_time_original = Column(String)
    date_time = Column(DateTime)
    settlement_id = Column(String)
    type = Column(String)
    order_id = Column(String)
    sku = Column(String)
    quantity = Column(Integer)  # source DF checked and all values are ints.
    marketplace = Column(String)
    fulfilment = Column(String)
    country_code = Column(String(2))
    source_file = Column(String)
    source_id = Column(Integer, ForeignKey(SourceMetaDataTable.source_id))
    date_inserted = Column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False,
    )

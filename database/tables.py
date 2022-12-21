from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    BigInteger,
    ForeignKey,
    Float,
    Date,
)
from sqlalchemy.sql import func

from database.base import Base
from definitions.schemas import Schemas

from sqlalchemy.types import BIGINT


class SourceMetaDataTable(Base):
    __tablename__ = "dim_raw_source_metadata"
    __table_args__ = {
        "schema": Schemas.RAW.value,
        # "extend_existing": True,
    }

    source_id = Column(BIGINT, primary_key=True, unique=True)
    source_name = Column(String, nullable=False)
    source_type = Column(String, nullable=False)
    source_filename = Column(String)
    date_inserted = Column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False,
    )


class ExternalPDFReimbursementHeaders(Base):
    __tablename__ = "external_reimbursement_headers"
    __table_args__ = {"schema": Schemas.RAW.value}

    unique_id = Column(BIGINT, primary_key=True, autoincrement=True, unique=True)
    internal_id = Column(BIGINT, unique=True)
    hash_id = Column(BIGINT)
    reimbursement_number = Column(String)
    order_number = Column(String)
    date_document = Column(Date)
    net_total = Column(Float)
    vat_amount = Column(Float)
    total = Column(Float)
    filename = Column(String)
    foldername = Column(String)
    file_type = Column(String)
    date_filename = Column(Date)
    reimbursement_number_filename = Column(String)
    order_number_filename = Column(String)
    pdf_text = Column(String)
    notes = Column(String)
    source_id = Column(BIGINT, ForeignKey(SourceMetaDataTable.source_id))
    date_inserted = Column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False,
    )


class ExternalPDFReimbursementItems(Base):
    __tablename__ = "external_reimbursement_items"
    __table_args__ = {"schema": Schemas.RAW.value}

    unique_id = Column(BIGINT, primary_key=True, autoincrement=True, unique=True)
    hash_id = Column(BIGINT)
    internal_id = Column(
        BIGINT, ForeignKey(ExternalPDFReimbursementHeaders.internal_id)
    )
    reimbursement_number = Column(String)
    item_nr = Column(Integer)
    quantity = Column(Integer)
    article_id = Column(String)
    description = Column(String)
    vat = Column(String)
    item_price = Column(Float)
    total_price = Column(Float)


class ExternalPDFInvoiceHeaders(Base):
    __tablename__ = "external_invoice_headers"
    __table_args__ = {"schema": Schemas.RAW.value}

    unique_id = Column(BIGINT, primary_key=True, autoincrement=True, unique=True)
    internal_id = Column(BIGINT, unique=True)
    # hash_id = Column(BIGINT)
    invoice_number = Column(String)
    order_number = Column(String)
    date_document = Column(Date)
    net_total = Column(Float)
    vat_amount = Column(Float)
    total = Column(Float)
    filename = Column(String)
    foldername = Column(String)
    file_type = Column(String)
    date_filename = Column(Date)
    invoice_number_filename = Column(String)
    order_number_filename = Column(String)
    pdf_text = Column(String)
    notes = Column(String)
    source_id = Column(BIGINT, ForeignKey(SourceMetaDataTable.source_id))
    date_inserted = Column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False,
    )


class ExternalPDFInvoiceItems(Base):
    __tablename__ = "external_invoice_items"
    __table_args__ = {"schema": Schemas.RAW.value}

    unique_id = Column(BIGINT, primary_key=True, autoincrement=True, unique=True)
    hash_id = Column(BIGINT)
    internal_id = Column(BIGINT, ForeignKey(ExternalPDFInvoiceHeaders.internal_id))
    invoice_number = Column(String)
    item_nr = Column(Integer)
    quantity = Column(Integer)
    article_id = Column(String)
    description = Column(String)
    vat = Column(String)
    item_price = Column(Float)
    total_price = Column(Float)


class ExternalInvoices(Base):
    __tablename__ = "external_invoices"
    __table_args__ = {"schema": Schemas.RAW.value}

    # TODO:
    unique_id = Column(BIGINT, primary_key=True, autoincrement=True, unique=True)
    hash_id = Column(BIGINT)
    record_type = Column(String)
    invoice_number = Column(String)
    currency = Column(String)
    total = Column(Float)
    credit_voucher = Column(String)
    shipping_method_order = Column(String)
    invoice_create_date = Column(Date)
    payment_method_order = Column(String)
    date_last_payment = Column(Date)
    total_payment_amount = Column(Float)
    total_invoice_correction = Column(Float)
    customer_number_order = Column(String)
    order_number = Column(String)
    order_create_date = Column(Date)
    external_order_number = Column(String)
    platform = Column(String)
    shipping_method_first_package = Column(String)
    tracking_number_first_package = Column(String)
    date_shipment_first_package = Column(String)
    date_inserted = Column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False,
    )


class AmazonSalesTable(Base):
    __tablename__ = "amazon_sales_data"
    __table_args__ = {"schema": Schemas.RAW.value}

    unique_id = Column(BIGINT, primary_key=True, autoincrement=True, unique=True)
    hash_id = Column(BIGINT)
    date_time_original = Column(String)
    date_time = Column(DateTime)
    settlement_id = Column(String)
    type = Column(String)
    order_id = Column(String)
    sku = Column(String)
    quantity = Column(Integer)  # source DF checked and all values are ints.
    total_price = Column(Float)
    marketplace = Column(String)
    fulfilment = Column(String)
    country_code = Column(String(2))
    currency = Column(String(3))
    source_file = Column(String)
    source_id = Column(BIGINT, ForeignKey(SourceMetaDataTable.source_id))
    date_inserted = Column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False,
    )

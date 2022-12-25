from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
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
    hash_id = Column(BIGINT, nullable=False)
    internal_id = Column(
        BIGINT, ForeignKey(ExternalPDFReimbursementHeaders.internal_id)
    )
    reimbursement_number = Column(String)
    item_nr = Column(Integer, nullable=False)
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
    hash_id = Column(BIGINT, nullable=False)
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
    source_id = Column(BIGINT, ForeignKey(SourceMetaDataTable.source_id))
    date_inserted = Column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False,
    )


class ExternalReimbursements(Base):
    __tablename__ = "external_reimbursements"
    __table_args__ = {"schema": Schemas.RAW.value}

    unique_id = Column(BIGINT, primary_key=True, autoincrement=True, unique=True)
    hash_id = Column(BIGINT)
    record_type = Column(String)
    reimbursement_number = Column(String)
    currency = Column(String)
    total_invoice_correction = Column(Float)
    total_order = Column(Float)
    shipping_method_order = Column(String)
    invoice_create_date = Column(DateTime)
    payment_method_order = Column(String)
    customer_number_order = Column(String)
    order_number = Column(String)
    order_create_date = Column(DateTime)
    external_order_number = Column(String)
    platform = Column(String)
    invoice_number = Column(String)
    source_id = Column(BIGINT, ForeignKey(SourceMetaDataTable.source_id))
    date_inserted = Column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False,
    )


class AmazonSalesTable(Base):
    __tablename__ = "amazon_sales_data"
    __table_args__ = {"schema": Schemas.RAW.value}

    unique_id = Column(BIGINT, primary_key=True, autoincrement=True, unique=True)
    hash_id = Column(BIGINT, nullable=False)
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


class ReturnedFromAmazon(Base):
    __tablename__ = "returned_from_amazon"
    __table_args__ = {"schema": Schemas.RAW.value}

    unique_id = Column(BIGINT, primary_key=True, autoincrement=True, unique=True)
    request_date = Column(DateTime)
    order_id = Column(String)
    order_type = Column(String)
    service_speed = Column(String)
    order_status = Column(String)
    last_updated_date = Column(DateTime)
    sku = Column(String)
    fnsku = Column(String)
    disposition = Column(String)
    requested_quantity = Column(Integer)
    cancelled_quantity = Column(Integer)
    disposed_quantity = Column(Integer)
    shipped_quantity = Column(Integer)
    in_process_quantity = Column(Integer)
    removal_fee = Column(Float)
    currency = Column(String)
    source_id = Column(BIGINT, ForeignKey(SourceMetaDataTable.source_id))
    date_inserted = Column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False,
    )


class ArticleShipmentInfo(Base):
    __tablename__ = "article_shipment_info"
    __table_args__ = {"schema": Schemas.RAW.value}

    unique_id = Column(BIGINT, primary_key=True, autoincrement=True, unique=True)
    sku = Column(String, nullable=False)
    article_type = Column(String, nullable=False)
    shipment_type = Column(String)
    article_net_price = Column(Float)
    max_items_per_shipment = Column(Integer)
    de_per_unit_shipment_price = Column(Float)
    at_per_unit_shipment_price = Column(Float)
    fr_per_unit_shipment_price = Column(Float)
    it_per_unit_shipment_price = Column(Float)
    es_per_unit_shipment_price = Column(Float)
    nl_per_unit_shipment_price = Column(Float)
    pl_per_unit_shipment_price = Column(Float)
    se_per_unit_shipment_price = Column(Float)
    uk_per_unit_shipment_price = Column(Float)
    source_id = Column(BIGINT, ForeignKey(SourceMetaDataTable.source_id))
    date_inserted = Column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False,
    )

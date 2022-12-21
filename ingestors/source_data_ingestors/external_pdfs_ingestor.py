import os
from typing import Union
import pandas as pd

from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import postgresql

from database.tables import (
    SourceMetaDataTable,
    ExternalPDFReimbursementHeaders,
    ExternalPDFReimbursementItems,
    ExternalPDFInvoiceHeaders,
    ExternalPDFInvoiceItems,
)

# from database.base import engine
from definitions.schemas import Schemas

from definitions.common import (
    SourceTypes,
    SourceNames,
    InvoiceHeaderTableColumns,
    ReimbursementHeaderTableColumns,
    InvoiceItemTableColumns,
    ReimbursementItemTableColumns,
)
from utils.common import create_int_hash_from_df_row

from ingestors.base_ingestor import BaseIngestor

import logging

logger = logging.getLogger()


class ExternalInvoicesReimbursementsIngestor(BaseIngestor):
    file_type = None
    header_table_name = ""
    item_table_name = ""
    source_type = SourceTypes.extracted_pdf_csv.value
    source_name = SourceNames.carpets_external.value

    def __init__(self, *, file_type: Union["RE", "GS"], engine):
        self.file_type = file_type
        if not self.file_type or self.file_type not in ["RE", "GS"]:
            raise Exception(
                f"Cannot create ingestor without correct type: {self.file_type}"
            )
        print(f"Starting data ingestor for External data of type: {self.file_type}...")
        self.header_table_name = (
            ExternalPDFInvoiceHeaders.__tablename__
            if self.file_type == "RE"
            else ExternalPDFReimbursementHeaders.__tablename__
        )
        self.item_table_name = (
            ExternalPDFInvoiceItems.__tablename__
            if self.file_type == "RE"
            else ExternalPDFReimbursementItems.__tablename__
        )
        data_folders = [i[0] for i in os.walk("data/external_invoices")]
        monthly_pdf_invoices = []
        for folder in data_folders:
            if self.file_type in folder and "combined_data.csv" in os.listdir(folder):
                monthly_df = pd.read_csv(
                    os.path.join(os.getcwd(), folder, "combined_data.csv")
                )
                monthly_pdf_invoices.append(monthly_df)
        all_pdf_invoices = pd.concat(monthly_pdf_invoices, ignore_index=True)

        print(
            CreateTable(SourceMetaDataTable.__table__).compile(
                dialect=postgresql.dialect()
            )
        )
        print(
            CreateTable(ExternalPDFReimbursementHeaders.__table__).compile(
                dialect=postgresql.dialect()
            )
        )

        self._separate_headers_and_items(all_pdf_invoices)
        self.add_source_metadata(engine)
        self.insert_into_db(engine)

    def _separate_headers_and_items(self, pdf_invoices: pd.DataFrame):
        print(f"pdf_invoices.columns: {pdf_invoices.columns}")
        if self.file_type == "RE":
            pdf_invoices["internal_id"] = pdf_invoices[InvoiceHeaderTableColumns].apply(
                lambda row: create_int_hash_from_df_row(row), axis=1
            )
            self.data_headers = pdf_invoices[
                [*InvoiceHeaderTableColumns, "internal_id", "pdf_text"]
            ].drop_duplicates()
            self.data_items = pdf_invoices[InvoiceItemTableColumns].copy()
        else:
            pdf_invoices["internal_id"] = pdf_invoices[
                ReimbursementHeaderTableColumns
            ].apply(lambda row: create_int_hash_from_df_row(row), axis=1)
            self.data_headers = pdf_invoices[
                [*ReimbursementHeaderTableColumns, "internal_id", "pdf_text"]
            ].drop_duplicates()
            self.data_items = pdf_invoices[ReimbursementItemTableColumns].copy()

    def add_source_metadata(self, engine):
        self.source_data = pd.DataFrame(self.data_headers["foldername"].unique())
        self.source_data.rename(
            columns={0: SourceMetaDataTable.source_filename.name}, inplace=True
        )
        self.source_data[SourceMetaDataTable.source_type.name] = self.source_type
        self.source_data[SourceMetaDataTable.source_name.name] = self.source_name
        self.source_data[SourceMetaDataTable.source_id.name] = self.source_data.apply(
            lambda row: create_int_hash_from_df_row(row), axis=1
        )

        self.source_data.to_sql(
            name=SourceMetaDataTable.__tablename__,
            con=engine,
            schema=Schemas.RAW.value,
            if_exists="append",
            index=False,
        )

    def insert_into_db(self, engine):
        self.data_headers = self.data_headers.merge(
            self.source_data,
            how="inner",
            left_on="foldername",
            right_on=SourceMetaDataTable.source_filename.name,
        )
        self.data_headers.drop(
            columns=[
                c.name
                for c in SourceMetaDataTable.__table__.columns
                if c.name
                not in (
                    SourceMetaDataTable.source_id.name,
                    SourceMetaDataTable.date_inserted.name,
                )
            ],
            axis=1,
            inplace=True,
        )

        self.data_headers.to_sql(
            name=self.header_table_name,
            con=engine,
            schema=Schemas.RAW.value,
            if_exists="append",
            index=False,
        )
        self.data_items.to_sql(
            name=self.item_table_name,
            con=engine,
            schema=Schemas.RAW.value,
            if_exists="append",
            index=False,
        )

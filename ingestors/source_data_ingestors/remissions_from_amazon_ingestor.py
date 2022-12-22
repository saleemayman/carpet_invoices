import os
from typing import Union

import datetime
import csv
import pandas as pd

from database.tables import (
    SourceMetaDataTable,
    ReturnedFromAmazon,
)

from database.base import engine
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

logger = logging.getLogger("root")


class ReturnsFromAmazonIngestor(BaseIngestor):
    table_name = ReturnedFromAmazon.__tablename__
    source_type = SourceTypes.original_csv_xl.value
    source_name = SourceNames.amazon_aws.value

    def __init__(self):
        csv_path = os.path.join(
            os.getcwd(), "data/returns_amazon/remissions_from_amazon.csv"
        )
        if not os.path.exists(csv_path):
            raise Exception(f"Path does not exist: {csv_path}")
        logger.info(f"Starting data ingestor for remissions from Amazon data...")
        self._read_and_transform_data(csv_path)
        self.add_source_metadata()
        self.insert_into_db()

    def _read_and_transform_data(self, csv_path: str):
        data = []
        lines = []
        with open(csv_path) as file:
            for line in file:
                row_data = line.rstrip(";\n").split(",")
                row_data = [column_value.strip('"') for column_value in row_data]
                lines.append(row_data)
        data_headers = lines[0]
        data_headers = [header.replace("-", "_") for header in data_headers]
        lines = lines[1:].copy()
        for line in lines:
            if len(line) == len(data_headers):
                data.append(line)
        data_df = pd.DataFrame(data, columns=data_headers)
        for column in data_df.columns:
            if "date" in column:
                data_df[column] = (
                    data_df[column]
                    .astype(str)
                    .apply(
                        lambda d: datetime.datetime.strptime(d, "%Y-%m-%dT%H:%M:%S%z")
                    )
                )
                continue
            if "quantity" in column:
                data_df[column] = pd.to_numeric(data_df[column], errors="coerce")
                data_df[column].fillna(0, inplace=True)
                data_df[column] = data_df[column].astype(int)
                continue
            if "removal_fee" == column:
                data_df[column] = pd.to_numeric(data_df[column], errors="coerce")
                data_df[column].fillna(0, inplace=True)
                continue
        self.data = data_df.copy()

    def add_source_metadata(self):
        self.source_data = pd.DataFrame(
            {
                "source_filename": ["remissions_from_amazon"],
                "source_type": [self.source_type],
                "source_name": [self.source_name],
            }
        )
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

    def insert_into_db(self):
        self.data = self.data.merge(
            self.source_data,
            how="cross",
        )
        self.data.drop(
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

        self.data.to_sql(
            name=self.table_name,
            con=engine,
            schema=Schemas.RAW.value,
            if_exists="append",
            index=False,
        )

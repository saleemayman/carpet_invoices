import os
import logging
import pandas as pd

from database.tables import AmazonSalesTable, SourceMetaDataTable

from database.base import engine
from definitions.schemas import Schemas

from definitions.common import SourceTypes, SourceNames
from utils.common import create_int_hash_from_df_row

from ingestors.base_ingestor import BaseIngestor

logger = logging.getLogger()


class AmazonSalesSourceIngestor(BaseIngestor):
    table_name = AmazonSalesTable.__tablename__
    source_type = SourceTypes.original_csv.value
    source_name = SourceNames.amazon_aws.value

    def __init__(self):
        print("Starting data ingestor for Amazon sales data...")
        csv_path = os.path.join(
            os.getcwd(), "data/amazon_sales/all_sales_data_combined.csv"
        )
        if os.path.exists(csv_path):
            self.data = pd.read_csv(csv_path)
        else:
            raise Exception(f"Path does not exist: {csv_path}")
        self.add_source_metadata()
        self.insert_into_db()

    def add_source_metadata(self):
        self.source_data = pd.DataFrame(self.data["source_file"].unique())
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

    def insert_into_db(self):
        self.data = self.data.merge(
            self.source_data,
            how="inner",
            left_on="source_file",
            right_on=SourceMetaDataTable.source_filename.name,
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

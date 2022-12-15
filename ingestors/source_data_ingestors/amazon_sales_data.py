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
    source_type = SourceTypes.csv.value
    source_name = SourceNames.amazon_aws.value

    def __init__(self):
        csv_path = os.path.join(
            "data/amazon_sales/all_sales_data.csv"
        )
        self.data = pd.read_csv(csv_path)

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

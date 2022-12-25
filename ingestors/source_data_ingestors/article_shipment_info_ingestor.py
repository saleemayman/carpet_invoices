import os

import pandas as pd

from database.tables import (
    SourceMetaDataTable,
    ArticleShipmentInfo,
)

from database.base import engine
from definitions.schemas import Schemas

from definitions.common import (
    SourceTypes,
    SourceNames,
    ArticleShipmentInfoColumnMapping,
)
from utils.common import create_int_hash_from_df_row

from ingestors.base_ingestor import BaseIngestor

import logging

logger = logging.getLogger("root")


class ArticleShipmentInfoIngestor(BaseIngestor):
    table_name = ArticleShipmentInfo.__tablename__
    source_type = SourceTypes.original_csv_xl.value
    source_name = SourceNames.self_enriched.value

    def __init__(self):
        csv_path = os.path.join(
            os.getcwd(), "data/amazon_sales/220914_SKU_Artikelpreise_Versandpreise.csv"
        )
        if not os.path.exists(csv_path):
            raise Exception(f"Path does not exist: {csv_path}")

        logger.info("Starting data ingestor for Article shipment price info...")
        self.data = pd.read_csv(csv_path, encoding="utf-16")
        self.data.rename(columns=ArticleShipmentInfoColumnMapping, inplace=True)
        self.add_source_metadata()
        self.insert_into_db()

    def add_source_metadata(self):
        self.source_data = pd.DataFrame(
            {
                "source_filename": ["220914_SKU_Artikelpreise_Versandpreise"],
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

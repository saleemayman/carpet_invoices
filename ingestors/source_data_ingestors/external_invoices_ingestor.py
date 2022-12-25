import os
from typing import Union
import pandas as pd


from database.tables import (
    SourceMetaDataTable,
    ExternalInvoices,
    ExternalReimbursements,
)

from database.base import engine
from definitions.schemas import Schemas

from definitions.common import (
    SourceTypes,
    SourceNames,
)
from utils.common import create_int_hash_from_df_row

from ingestors.base_ingestor import BaseIngestor

import logging

logger = logging.getLogger("root")


class ExternalInvoicesReimbursementsIngestor(BaseIngestor):
    source_type = SourceTypes.original_csv_xl.value
    source_name = SourceNames.carpets_external.value

    def __init__(self, *, file_type: Union["RE", "GS"]):
        logger.info(f"Starting ingestor for External invoices of type: {file_type} ...")
        self.file_type = file_type
        if not self.file_type or self.file_type not in ["RE", "GS"]:
            raise Exception(
                f"Cannot create ingestor without correct type: {self.file_type}"
            )
        self.table_name = (
            ExternalInvoices.__tablename__
            if self.file_type == "RE"
            else ExternalReimbursements.__tablename__
        )
        data_folders = [i[0] for i in os.walk("data/external_invoices")]
        monthly_data = []
        for folder in data_folders:
            if "RE" not in folder and "GS" not in folder:
                for file in os.listdir(folder):
                    if self.file_type == "RE":
                        if "rgexport" in file.lower():
                            logger.info(f"Reading monthly CSV from: {file}")
                            monthly_df = pd.read_csv(
                                os.path.join(os.getcwd(), folder, file)
                            )
                            monthly_df["source_file"] = os.path.join(folder, file)
                            monthly_data.append(monthly_df)
                    else:
                        if "gsexport" in file.lower():
                            logger.info(f"Reading monthly CSV from: {file}")
                            monthly_df = pd.read_csv(
                                os.path.join(os.getcwd(), folder, file)
                            )
                            monthly_df["source_file"] = os.path.join(folder, file)
                            monthly_data.append(monthly_df)
        if len(monthly_data) > 0:
            self.data = pd.concat(monthly_data, ignore_index=True)
        else:
            raise Exception("No monthly invoice or reimbursement files found.")
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
                *[
                    c.name
                    for c in SourceMetaDataTable.__table__.columns
                    if c.name
                    not in (
                        SourceMetaDataTable.source_id.name,
                        SourceMetaDataTable.date_inserted.name,
                    )
                ],
                "source_file",
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

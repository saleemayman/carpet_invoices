import os

from database.base import db_session
from database.db import init_db
from sqlalchemy import create_engine

# from definitions.data_ingestors import SourceDataIngestors

from ingestors.source_data_ingestors.amazon_sales_data import AmazonSalesSourceIngestor
from ingestors.source_data_ingestors.external_pdfs_ingestor import (
    ExternalInvoicesReimbursementsIngestor,
)

import logging

logger = logging.getLogger()

DB_PORT = os.environ["DB_PORT"] or 5432
DB_HOST = os.environ["DB_HOST"] or "postgres"
DB_USER = os.environ["POSTGRES_USER"] or "postgres"
DB_PASSWORD = os.environ["POSTGRES_PASSWORD"] or "postgres"
DB_NAME = os.environ["POSTGRES_DB"] or "postgres"


def setup():
    connection_string = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    engine = create_engine(connection_string, echo=True)

    init_db(engine)

    AmazonSalesSourceIngestor(engine)
    ExternalInvoicesReimbursementsIngestor(file_type="RE", engine=engine)
    ExternalInvoicesReimbursementsIngestor(file_type="GS", engine=engine)

    db_session.commit()


if __name__ == "__main__":
    setup()

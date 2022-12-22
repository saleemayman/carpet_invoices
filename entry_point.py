import os
import sys

from database.base import db_session
from database.db import init_db
from sqlalchemy import create_engine

# from definitions.data_ingestors import SourceDataIngestors
from database.base import engine

from ingestors.source_data_ingestors.amazon_sales_data import AmazonSalesSourceIngestor
from ingestors.source_data_ingestors.external_pdfs_ingestor import (
    ExternalInvoicesReimbursementsIngestor,
)

import logging
logging.basicConfig(
    format="%(asctime)s: %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)
logger = logging.getLogger(__file__)

# logger = logging.getLogger()

def setup():
    init_db()

    AmazonSalesSourceIngestor()
    ExternalInvoicesReimbursementsIngestor(file_type="RE")
    ExternalInvoicesReimbursementsIngestor(file_type="GS")

    db_session.commit()


if __name__ == "__main__":
    setup()

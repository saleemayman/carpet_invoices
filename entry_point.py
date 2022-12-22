import os
import sys

from database.base import db_session
from database.db import init_db
from sqlalchemy import create_engine

# from definitions.data_ingestors import SourceDataIngestors
from database.base import engine

from ingestors.source_data_ingestors.amazon_sales_data import AmazonSalesSourceIngestor
from ingestors.source_data_ingestors.external_pdfs_ingestor import (
    ExternalPDFInvoicesReimbursementsIngestor,
)
from ingestors.source_data_ingestors.external_invoices_ingestor import ExternalInvoicesReimbursementsIngestor
from ingestors.source_data_ingestors.remissions_from_amazon_ingestor import (
    ReturnsFromAmazonIngestor,
)
from ingestors.source_data_ingestors.article_shipment_info_ingestor import (
    ArticleShipmentInfoIngestor,
)

import logging

logging.basicConfig(
    format="%(asctime)s: %(message)s",
    level=logging.INFO,
    stream=sys.stderr,
)
logger = logging.getLogger("root")


def setup():
    logger.info("Initialising database...")

    init_db()

    AmazonSalesSourceIngestor()
    ExternalPDFInvoicesReimbursementsIngestor(file_type="RE")
    ExternalPDFInvoicesReimbursementsIngestor(file_type="GS")
    ExternalInvoicesReimbursementsIngestor(file_type="RE")
    ExternalInvoicesReimbursementsIngestor(file_type="GS")
    ReturnsFromAmazonIngestor()
    ArticleShipmentInfoIngestor()

    db_session.commit()


if __name__ == "__main__":
    setup()

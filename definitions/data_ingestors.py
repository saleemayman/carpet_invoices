from enum import Enum

from ingestors.source_data_ingestors.amazon_sales_data import AmazonSalesSourceIngestor


class SourceDataIngestors(Enum):
    AMAZON_SALES_INGESTOR = AmazonSalesSourceIngestor

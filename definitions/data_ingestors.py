from enum import Enum

from ingestors.source_data_ingestors.amazon_sales_data import AmazonSalesSourceIngestor
from ingestors.source_data_ingestors.external_pdfs_ingestor import ExternalInvoicesReimbursementsIngestor


class SourceDataIngestors(Enum):
    AMAZON_SALES_INGESTOR = AmazonSalesSourceIngestor()
    EXTERNAL_REMIBURSEMENT_PDFS_INGESTOR = ExternalInvoicesReimbursementsIngestor(file_type="GS")
    EXTERNAL_INVOICE_PDFS_INGESTOR = ExternalInvoicesReimbursementsIngestor(file_type="RE")

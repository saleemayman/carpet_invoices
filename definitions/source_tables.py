from enum import Enum

from database.tables import AmazonSalesTable, SourceMetaDataTable


class SourceTables(Enum):
    AMAZON_SALES_TABLE = AmazonSalesTable
    SOURCE_METADATA_TABLE = SourceMetaDataTable

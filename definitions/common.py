from enum import Enum


class SourceTypes(Enum):
    original_csv_xl = "original_csv_xl"
    extracted_pdf_csv = "extracted_pdf_csv"


class SourceNames(Enum):
    amazon_aws = "amazon_aws"
    carpets_external = "carpets_external"
    self_enriched = "self_enriched"


class ExternalDocumentType(Enum):
    invoice = "invoice"
    reimbursement = "reimbursement"


InvoiceHeaderTableColumns = [
    "invoice_number",
    "order_number",
    "date_document",
    "net_total",
    "vat_amount",
    "total",
    "filename",
    "foldername",
    "file_type",
    "date_filename",
    "invoice_number_filename",
    "order_number_filename",
    "notes",
]

ReimbursementHeaderTableColumns = [
    "reimbursement_number",
    "order_number",
    "date_document",
    "net_total",
    "vat_amount",
    "total",
    "filename",
    "foldername",
    "file_type",
    "date_filename",
    "reimbursement_number_filename",
    "order_number_filename",
    "notes",
]

InvoiceItemTableColumns = [
    "hash_id",
    "internal_id",
    "invoice_number",
    "item_nr",
    "quantity",
    "article_id",
    "description",
    "vat",
    "item_price",
    "total_price",
]

ReimbursementItemTableColumns = [
    "hash_id",
    "internal_id",
    "reimbursement_number",
    "item_nr",
    "quantity",
    "article_id",
    "description",
    "vat",
    "item_price",
    "total_price",
]

ArticleShipmentInfoColumnMapping = {
    "SKU": "sku",
    "Artikelart": "article_type",
    "Versandart": "shipment_type",
    "Artikelpreis Netto": "article_net_price",
    "Max Items / Shipment": "max_items_per_shipment",
    "Versandpreis pro Einheit - DE": "de_per_unit_shipment_price",
    "Versandpreis pro Einheit - AT": "at_per_unit_shipment_price",
    "Versandpreis pro Einheit - FR": "fr_per_unit_shipment_price",
    "Versandpreis pro Einheit - IT": "it_per_unit_shipment_price",
    "Versandpreis pro Einheit - ES": "es_per_unit_shipment_price",
    "Versandpreis pro Einheit - NL": "nl_per_unit_shipment_price",
    "Versandpreis pro Einheit - PL": "pl_per_unit_shipment_price",
    "Versandpreis pro Einheit - SE": "se_per_unit_shipment_price",
    "Versandpreis pro Einheit - UK": "uk_per_unit_shipment_price",
}

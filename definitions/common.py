from enum import Enum


class SourceTypes(Enum):
    original_csv = "original_csv"
    extracted_pdf_csv = "extracted_pdf_csv"


class SourceNames(Enum):
    amazon_aws = "amazon_aws"
    carpets_external = "carpets_external"

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
    # "pdf_text",
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
    # "pdf_text",
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

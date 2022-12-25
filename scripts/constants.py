import os
import re

PARENT_DIR = os.path.abspath(os.pardir)
AMAZON_SALES_DATA_DIR = os.path.join(
    os.getcwd(), "../tara_data_backup", "TaraCarpetRugs", "Transaktionen_Amazon"
)

COUNTRY_TO_COLUMNS_MAPPING = {
    "UK": {
        "date/time": "date_time_original",
        "settlement id": "settlement_id",
        "type": "type",
        "order id": "order_id",
        "sku": "sku",
        "quantity": "quantity",
        "marketplace": "marketplace",
        "fulfilment": "fulfilment",
        "total": "total_price",
    },
    "NL": {
        "datum/tijd": "date_time_original",
        "schikkings-ID": "settlement_id",
        "type": "type",
        "bestelnummer": "order_id",
        "sku": "sku",
        "aantal": "quantity",
        "marketplace": "marketplace",
        "fulfillment": "fulfilment",
        "totaal": "total_price",
    },
    "FR": {
        "date/heure": "date_time_original",
        "numéro de versement": "settlement_id",
        "type": "type",
        "numéro de la commande": "order_id",
        "sku": "sku",
        "quantité": "quantity",
        "Marketplace": "marketplace",
        "traitement": "fulfilment",
        "total": "total_price",
    },
    "SE": {
        "datum/tid": "date_time_original",
        "reglerings-id": "settlement_id",
        "typ": "type",
        "beställnings-id": "order_id",
        "sku": "sku",
        "antal": "quantity",
        "marknadsplats": "marketplace",
        "leverans": "fulfilment",
        "totalt": "total_price",
    },
    "IT": {
        "Data/Ora:": "date_time_original",
        "Numero pagamento": "settlement_id",
        "Tipo": "type",
        "Numero ordine": "order_id",
        "SKU": "sku",
        "Quantità": "quantity",
        "Marketplace": "marketplace",
        "Gestione": "fulfilment",
        "totale": "total_price",
    },
    "DE": {
        "Datum/Uhrzeit": "date_time_original",
        "Abrechnungsnummer": "settlement_id",
        "Typ": "type",
        "Bestellnummer": "order_id",
        "SKU": "sku",
        "Menge": "quantity",
        "Marketplace": "marketplace",
        "Versand": "fulfilment",
        "Gesamt": "total_price",
    },
    "PL": {
        "data/godzina": "date_time_original",
        "identyfikator rozliczenia": "settlement_id",
        "typ": "type",
        "identyfikator zamówienia": "order_id",
        "sku": "sku",
        "ilość": "quantity",
        "rynek": "marketplace",
        "realizacja": "fulfilment",
        "suma": "total_price",
    },
    "ES": {
        "fecha y hora": "date_time_original",
        "identificador de pago": "settlement_id",
        "tipo": "type",
        "número de pedido": "order_id",
        "sku": "sku",
        "cantidad": "quantity",
        "web de Amazon": "marketplace",
        "gestión logística": "fulfilment",
        "total": "total_price",
    },
}

# regex patterns for parsing PDF files
file_date_regx = re.compile(r"^(?:.*)?(20[0-9]{6})")
invoice_nr_regx = re.compile(r"^(?:.*)?(RE[0-9]{6})")
reimbursement_nr_regx = re.compile(r"^(?:.*)?(GS[0-9]{6})")
au_order_nr_regx = re.compile(r"^(?:.*)?(AU[0-9]{4,5})")
real_order_nr_regx = re.compile(r"^(?:.*)?(REAL-ADA-[A-Z0-9]{7})")
shopify_order_nr_regx = re.compile(r"^(?:.*)?(SHOPIFY-ADA-[0-9]{13})")
amazon_order_nr_regx = re.compile(r"^(?:.*)?(AMZ-ADA-[0-9]{3}-[0-9]{7}-[0-9]{7})")
ebay_order_nr_regx = re.compile(r"^(?:.*)?(EBAY-DE-ADA-[0-9]{2}-[0-9]{5}-[0-9]{5})")

# pattern for date in the invoice
invoice_date_regx = re.compile(r"^([0-9]{2}\.[0-9]{2}\.[0-9]{4})$")

# standard complete line case
standard_row_all_7_columns_regx = re.compile(
    r"^([0-9]{1,3})"  # item_nr
    r"\s([0-9]{1,3}(?:\s[stück]{3,5})?)"  # quantity
    r"\s([0-9]{5}\-[0-9]{2}\-[0-9]{2}|H[0-9]{5}|[^\s]+(?=\s))"  # article_nr
    r"\s(.*?(?=\s[0-9]{1,2}(?:,00)?%))"  # description
    # r"\s(.*?(?=(?:\s[0-9]{1,2}(?:,00)?%)?\s(?:-)?[\.0-9]{1,6},[0-9]{2}))"  # description
    # r"\s([0-9]{1,2}(?:,00)?%)"    # vat
    r"(?:\s([0-9]{1,2}(?:,00)?%))?"  # vat
    r"\s((?:-)?[\.0-9]{1,6},[0-9]{2})"  # item_price
    r"\s((?:-)?[\.0-9]{1,6},[0-9]{2})$"  # total_price
)

# incomplete description case only
incomplete_row_4_columns_regx = re.compile(
    r"^([0-9]{1,3})"  # item_nr
    r"\s([0-9]{1,3}(?:\s[stück]{3,5})?)"  # quantity
    r"\s([0-9]{5}\-[0-9]{2}\-[0-9]{2}|H[0-9]{5}|[^\s]+)"  # article_nr
    r"\s(.*$)"  # description
)

# only description or ArtNr case
only_article_or_description_in_row_regx = re.compile(
    r"^([0-9]{1,3})"  # item_nr
    r"\s([0-9]{1,3}(?:\s[stück]{3,5})?)"  # quantity
    # r"\s(.*(?=\s[0-9]{1,2}(?:,00)?%))"    # article_nr or description
    r"\s(.*?(?=(?:\s[0-9]{1,2}(?:,00)?%)?\s(?:-)?[\.0-9]{1,6},[0-9]{2}))"  # description
    # r"\s([0-9]{1,2}(?:,00)?%)"    # vat
    r"(?:\s([0-9]{1,2}(?:,00)?%))?"  # vat
    r"\s((?:-)?[\.0-9]{1,6},[0-9]{2})"  # item_price
    r"\s((?:-)?[\.0-9]{1,6},[0-9]{2})$"  # total_price
)

# no description and ArtNr
neither_article_nor_description_in_row_regx = re.compile(
    r"^([0-9]{1,3})"  # item_nr
    r"\s([0-9]{1,3}(?:\s[stück]{3,5})?)"  # quantity
    # r"\s([0-9]{1,2}(?:,00)?%)"    # vat
    r"(?:\s([0-9]{1,2}(?:,00)?%))?"  # vat
    r"\s((?:-)?[\.0-9]{1,6},[0-9]{2})"  # item_price
    r"\s((?:-)?[\.0-9]{1,6},[0-9]{2})$"  # total_price
)

# incomplete row: split description
remaining_description_row_regx = re.compile(r"^(?:(?!.*%).*)$")

# incomplete row: final 3 columns
incomplete_row_last_3_columns_regx = re.compile(
    r"^([0-9]{1,2}(?:,00)?%)"
    r"\s((?:-)?[\.0-9]{1,6},[0-9]{2})"
    r"\s((?:-)?[\.0-9]{1,6},[0-9]{2})$"
)

# invoice net total or end
invoice_net_total_regx = re.compile(
    r"^Gesamt\sNetto\s"
    r"(?:\([0-9]{1,2}(?:,00)?%\))?\s"  # VAT value, sometimes not there
    r"(?:€\s)?((?:-)?[\.0-9]{1,6},[0-9]{2})(?:\s€)?.*$"  # netto invoice amount, will be extracted
)

# VAT amount
vat_amount_regx = re.compile(
    r"^zzgl(?:\.)?\s(?:(?:\()?[0-9]{1,2}(?:,00)?%(?:\))?)?\sMw(?:\.)?St(?:\.)?\s"
    r"(?:€\s)?((?:-)?[\.0-9]{1,6},[0-9]{2})(?:\s€)?.*$"  # vat amount
)

# invoice total with vat
invoice_total_regx = re.compile(
    r"^Gesamtbetrag\s(?:€\s)?((?:-)?[\.0-9]{1,6},[0-9]{2})(?:\s€)?.*$"
)


# column mapping for RgExport invoice files
MONTHLY_INVOICE_COLUMN_MAPPING = {
    "Satzart": "record_type",
    "Belegnummer": "invoice_number",
    "Währung ISO": "currency",
    "Gesamtsumme": "total",
    "Guthaben Gutschein": "credit_voucher",
    "Versandart Auftrag": "shipping_method_order",
    "Erstelldatum Rechnung": "invoice_create_date",
    "Zahlungsart Auftrag": "payment_method_order",
    "Datum letzte Zahlung": "date_last_payment",
    "Zahlbetrag gesamt": "total_payment_amount",
    "Gesamtsumme Rechnungskorrektur": "total_invoice_correction",
    "Kundennummer Auftrag": "customer_number_order",
    "Auftragsnummer": "order_number",
    "Erstelldatum Auftrag": "order_create_date",
    "Externe Auftragsnummer": "external_order_number",
    "Plattform": "platform",
    "Versandart Erstes Paket": "shipping_method_first_package",
    "Sendungsnummer Erstes Paket": "tracking_number_first_package",
    "Versanddatum Erstes Paket": "date_shipment_first_package",
}

# column mapping for GsExport invoice files
MONTHLY_REIMBURSEMENT_COLUMN_MAPPING = {
    "Satzart": "record_type",
    "Belegnummer": "reimbursement_number",
    "Währung ISO": "currency",
    "Gesamtsumme Rechnungskorrektur": "total_invoice_correction",
    "Gesamtsumme Auftrag": "total_order",
    "Versandart Auftrag": "shipping_method_order",
    "Erstelldatum Rechnung": "invoice_create_date",
    "Zahlungsart Auftrag": "payment_method_order",
    "Kundennummer Auftrag": "customer_number_order",
    "Auftragsnummer": "order_number",
    "Erstelldatum Auftrag": "order_create_date",
    "Externe Auftragsnummer": "external_order_number",
    "Plattform": "platform",
    "Rechnungsnummer": "invoice_number",
}

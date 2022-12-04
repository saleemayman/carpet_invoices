import os
import sys

from os.path import dirname


def set_python_path():
    sys.path.append(dirname(dirname(dirname(__file__))))


PARENT_DIR = os.path.abspath(os.pardir)  # tara/
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
    },
}
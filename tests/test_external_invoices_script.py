import pytest

import pandas as pd

from scripts.external_invoices_reimbursements import (
    get_invoice_reimbursement_table_from_extracted_text,
)


@pytest.fixture
def extracted_pdf_text():
    return [
        "This GmbH",
        "Fantastic Joe",
        "Hauptweg 1",
        "12345 Hauptstadt",
        "Deutschland",
        "Rechnungsnr. RE123456 bzgl. Auftragsnummer: AMZ-ADA-123-1234567-1234567",
        "Seite: 1",
        "External GmbH, Adolfstr. 88 , 12345 Keinstadt",
        "External GmbH",
        "Fantastic Doe",
        "Adolfstr. 88",
        "12345 Keinstadt",
        "Tel: 01234 1234567",
        "Fax: 01234 123456",
        "Web: https://external-carpets.com",
        "E-Mail: info@external-carpets.com",
        "Bearbeiter: Administrator",
        "Bankverbindung: Sparkasse IBAN: DE12 1234 1234 1234 5678 90 BIC: ABCDEFG1HIJ USt-ID: DE123456789 Gläubiger-ID:",
        "Rechnung",
        "10.01.2021",
        "Kundennummer: ABC123",
        "Pos. Menge ArtNr Bezeichnung Ust. E-Preis G-Preis",
        "1 1 stk 12345-12-12 Description of some item 050x100 cm 19% 1,11 1,11",
        "2 1 stk H12345 Other description 100x100 cm rund 19% 2,00 2,00",
        "3 1 Versand GLS-DB 19% 10,00 10,00",
        "4 1 stk 12345-05-06 A very long description of some item",
        "which extends to next line 100x100 cm",
        "19% 88,88 88,88",
        "5 1 19% 0,00 0,00",
        "6 1 Versand 19% 10,00 10,00",
        "Gesamt Netto (19,00%) € 111,99",
        "zzgl. 19,00% MwSt. € 21,28",
        "Gesamtbetrag € 133,27",
        "Ihre Ust-ID: DE310123456",
        "Additional",
        "Notes about the invoice which need to be extracted",
        "completely as notes.",
        "Vielen Dank für Ihren Auftrag.\n",
    ]


def test_get_invoice_reimbursement_table_from_extracted_text(extracted_pdf_text):
    expected = {
        "date": "10.01.2021",
        "net_total": 111.99,
        "vat_amount": 21.28,
        "total": 133.27,
        "table_data": {
            "item_nr": [1, 2, 3, 4, 5, 6],
            "quantity": [1, 1, 1, 1, 1, 1],
            "article_id": [
                "12345-12-12",
                "H12345",
                "Versand",
                "12345-05-06",
                "",
                "",
            ],
            "description": [
                "Description of some item 050x100 cm",
                "Other description 100x100 cm rund",
                "GLS-DB",
                "A very long description of some item which extends to next line 100x100 cm",
                "",
                "Versand",
            ],
            "vat": ["19%", "19%", "19%", "19%", "19%", "19%"],
            "item_price": [1.11, 2.00, 10.00, 88.88, 0.00, 10.00],
            "total_price": [1.11, 2.00, 10.00, 88.88, 0.00, 10.00],
        },
        "notes": "Additional Notes about the invoice which need to be extracted completely as notes.",
        "extracted_metadata": {
            "invoice_nr_from_pdf": "RE123456",
            "order_nr_from_pdf": "AMZ-ADA-123-1234567-1234567",
            "reimbursement_nr_from_pdf": None,
        },
    }

    results = get_invoice_reimbursement_table_from_extracted_text(
        "test_file", extracted_pdf_text
    )
    results["table_data"] = results["table_data"].to_dict(orient="list")

    assert expected == results

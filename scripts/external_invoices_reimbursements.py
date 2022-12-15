import os
import re
import datetime
import math
from typing import List, Optional
from pathlib import Path
import warnings

from dataclasses import dataclass

import pandas as pd
import pypdfium2 as pdfium
from constants import (
    invoice_date_regx,
    standard_row_all_7_columns_regx,
    incomplete_row_4_columns_regx,
    only_article_or_description_in_row_regx,
    neither_article_nor_description_in_row_regx,
    remaining_description_row_regx,
    incomplete_row_last_3_columns_regx,
    invoice_net_total_regx,
    vat_amount_regx,
    invoice_total_regx,
    file_date_regx,
    invoice_nr_regx,
    reimbursement_nr_regx,
    au_order_nr_regx,
    real_order_nr_regx,
    shopify_order_nr_regx,
    amazon_order_nr_regx,
    ebay_order_nr_regx,
)

import logging

logger = logging.getLogger()

INVOICES_DIR = "/home/as/work/tara_data_backup/TaraCarpetRugs/Rechnungen_TaraCarpet"


# extract invoice items from pdf text if above failed
INVOICE_TABLE_COLUMNS = {
    "pos": "item_nr",
    "menge": "quantity",
    "artnr": "article_id",
    "bezeichnung": "description",
    "ust": "vat",
    "epreis": "item_price",
    "gpreis": "total_price",
}

NUMERIC_COLUMNS = [
    "quantity",
    "item_price",
    "total_price",
]


def parse_external_invoices_folder() -> dict:
    """Walks the invoices root folder containing folders for monthly data with below
    directory structure:
    .
    ├── GS
    │   └── many PDF files  # invoice table to be extracted from each
    ├── RE
    │   └── many PDF files  # invoice table to be extracted from each
    ├── GSExport.xlsx
    ├── RGExport.xlsx
    └── random_other_file
    The function will parse all monthly folders and all filepaths found while walking
    the folders - all files except system files (.DS_Store). Returns a dict as follows:
    {
        "YYYYMM" or "YYYYMM/GS" "YYYYMM/RE": {
            "files": []
            "num_files": int
        }
    }
    """
    invoices_data_folders = [i[0] for i in os.walk(INVOICES_DIR)]
    folders_metadata = {}
    for folder in invoices_data_folders:
        path_items = folder.split("/")
        starting_location = path_items.index("Rechnungen_TaraCarpet")
        folder_path_name = "/".join(path_items[starting_location + 1:])
        path_identifiers = path_items[starting_location + 1:]  # starting+1 till end
        folder_files = os.listdir(folder)
        if len(path_identifiers) > 0 and len(path_identifiers) < 3:
            folders_metadata[folder_path_name] = {
                "files": folder_files,
                "num_files": len(folder_files),
            }
        else:
            folders_metadata[folder_path_name] = {}
            print(f"Unexpected folder path: {folder}")
    return folders_metadata


@dataclass
class InvoiceReimbursement:
    filename: str
    invoice_nr: str
    reimbursement_nr: Optional[str]
    order_nr: str
    invoice_date: datetime.date
    table_data: pd.DataFrame
    vat: int
    total: float
    net_total: float
    notes: str


def parse_invoice_reimbursement_info_from_filename(folder_name: str, pdf_filename: str):
    file_date = file_date_regx.findall(pdf_filename)[0]
    if "RE" in folder_name:
        invoice_nr = invoice_nr_regx.findall(pdf_filename)[0]
    elif "GS" in folder_name:
        reimbursement_nr = reimbursement_nr_regx.findall(pdf_filename)[0]
    else:
        print(f"Not a valid directory. Not a invoice/reimbursement PDFs folder: {folder_name}")
    if amazon_order_nr_regx.match(pdf_filename):
        order_nr = amazon_order_nr_regx.findall(pdf_filename)[0]
    elif ebay_order_nr_regx.match(pdf_filename):
        order_nr = ebay_order_nr_regx.findall(pdf_filename)[0]
    elif shopify_order_nr_regx.match(pdf_filename):
        order_nr = shopify_order_nr_regx.findall(pdf_filename)[0]
    elif au_order_nr_regx.match(pdf_filename):
        order_nr = au_order_nr_regx.findall(pdf_filename)[0]
    else:
        order_nr = None
        print("Unexpected PDF filename. Cannot find Order Nr in " f"filename: {pdf_filename}")

    return {
        "type": "INVOICE" if "RE" in folder_name else "REIMBURSEMENT" if "GS" in folder_name else None,
        "date_filename": file_date,
        "order_nr": order_nr,
        "invoice_reimbursement_nr": invoice_nr
        if "RE" in folder_name
        else reimbursement_nr
        if "GS" in folder_name
        else None,
    }


def extract_text_from_pdfs(pdf_path: str):
    text = ""
    pdf = pdfium.PdfDocument(pdf_path)
    for i in range(len(pdf)):  # loop over all pages
        page = pdf.get_page(i)
        textpage = page.get_textpage()
        text += textpage.get_text()
        text += "\n"
        [g.close() for g in (textpage, page)]
    pdf.close()
    return text.split("\r\n")


def extract_invoice_metadata_from_pdf_text_line(line: str):
    invoice_nr_from_pdf = invoice_nr_regx.findall(line)[0] if invoice_nr_regx.match(line) else None
    reimbursement_nr_from_pdf = reimbursement_nr_regx.findall(line)[0] if reimbursement_nr_regx.match(line) else None
    if au_order_nr_regx.match(line):
        order_nr_from_pdf = au_order_nr_regx.findall(line)[0]
    elif real_order_nr_regx.match(line):
        order_nr_from_pdf = real_order_nr_regx.findall(line)[0]
    elif shopify_order_nr_regx.match(line):
        order_nr_from_pdf = shopify_order_nr_regx.findall(line)[0]
    elif amazon_order_nr_regx.match(line):
        order_nr_from_pdf = amazon_order_nr_regx.findall(line)[0]
    elif ebay_order_nr_regx.match(line):
        order_nr_from_pdf = ebay_order_nr_regx.findall(line)[0]
    else:
        order_nr_from_pdf = None

    return {
        "invoice_nr_from_pdf": invoice_nr_from_pdf,
        "order_nr_from_pdf": order_nr_from_pdf,
        "reimbursement_nr_from_pdf": reimbursement_nr_from_pdf,
    }


def get_invoice_reimbursement_table_from_extracted_text(
    file_name: str,
    pdf_text: List[str],
):
    print(f"Parsing: {file_name}, text: {pdf_text}")
    if "Rechnung" in pdf_text:
        heading_start_index = pdf_text.index("Rechnung")
    elif "RECHNUNGSKORREKTUR" in pdf_text:
        heading_start_index = pdf_text.index("RECHNUNGSKORREKTUR")
    else:
        raise Exception("Not able to find body containing table: {file_name}")
    for line in pdf_text[:heading_start_index]:
        if invoice_nr_regx.match(line) or reimbursement_nr_regx.match(line):
            extracted_metadata = extract_invoice_metadata_from_pdf_text_line(line)
        if re.match(r"^Seite:", line):
            break
    main_data_as_text = pdf_text[heading_start_index:]
    data_table_started = False
    is_file_totaled = False
    data_table_complete = False
    table_rows = []
    invoice_reimbursement_notes = []
    invoice_reimbursement_date = None
    net_total_amount = None
    vat_amount = None
    total_amount = None
    for row_index, row in enumerate(main_data_as_text):
        # print(f"row {row}")
        if (
            invoice_reimbursement_date is not None
            and net_total_amount is not None
            and vat_amount is not None
            and total_amount is not None
        ):
            is_file_totaled = True
        if invoice_date_regx.match(row):
            invoice_reimbursement_date = invoice_date_regx.findall(row)[0]
            # print(f"1.0")
            continue
        if re.match(r"^Pos\.\sMenge", row, re.IGNORECASE) and not data_table_complete:
            data_table_started = True
            is_invoice_item_complete = False
            # print(f"2.0")
            continue
        if data_table_started and not data_table_complete:
            if standard_row_all_7_columns_regx.match(row):
                columns_values = standard_row_all_7_columns_regx.findall(row)[0]
                table_rows.append(
                    {
                        "item_nr": columns_values[0],
                        "quantity": int(columns_values[1].split()[0]),
                        "article_id": columns_values[2],
                        "description": columns_values[3],
                        "vat": columns_values[4],
                        "item_price": float(columns_values[5].replace(".", "").replace(",", ".")),
                        "total_price": float(columns_values[6].replace(".", "").replace(",", ".")),
                    }
                )
                is_invoice_item_complete = True
                # print(f"3.1")
                continue
            if incomplete_row_4_columns_regx.match(row):
                incomplete_columns_values = incomplete_row_4_columns_regx.findall(row)[0]
                is_invoice_item_complete = False
                # print(f"3.1.2")
            if not is_invoice_item_complete:
                if (
                    remaining_description_row_regx.match(row)
                    and not incomplete_row_4_columns_regx.match(row)
                    and not incomplete_row_last_3_columns_regx.match(row)
                ):
                    remaining_description_column_value = row
                    # print(f"3.2")
                    continue
                if incomplete_row_last_3_columns_regx.match(row):
                    last_3_columns_values = incomplete_row_last_3_columns_regx.findall(row)[0]
                    table_rows.append(
                        {
                            "item_nr": incomplete_columns_values[0],
                            "quantity": int(incomplete_columns_values[1].split()[0]),
                            "article_id": incomplete_columns_values[2],
                            "description": incomplete_columns_values[3]
                            + (" " + remaining_description_column_value or ""),
                            "vat": last_3_columns_values[0],
                            "item_price": float(last_3_columns_values[1].replace(".", "").replace(",", ".")),
                            "total_price": float(last_3_columns_values[2].replace(".", "").replace(",", ".")),
                        }
                    )
                    is_invoice_item_complete = True
                    # print(f"last 3 columns done")
                    continue
            if only_article_or_description_in_row_regx.match(row):
                columns_values = only_article_or_description_in_row_regx.findall(row)[0]
                table_rows.append(
                    {
                        "item_nr": columns_values[0],
                        "quantity": int(columns_values[1].split()[0]),
                        "article_id": "",
                        "description": columns_values[2],
                        "vat": columns_values[3],
                        "item_price": float(columns_values[4].replace(".", "").replace(",", ".")),
                        "total_price": float(columns_values[5].replace(".", "").replace(",", ".")),
                    }
                )
                is_invoice_item_complete = True
                # print(f"3.5")
                continue
            if neither_article_nor_description_in_row_regx.match(row):
                columns_values = neither_article_nor_description_in_row_regx.findall(row)[0]
                table_rows.append(
                    {
                        "item_nr": columns_values[0],
                        "quantity": int(columns_values[1].split()[0]),
                        "article_id": "",
                        "description": "",
                        "vat": columns_values[2],
                        "item_price": float(columns_values[3].replace(".", "").replace(",", ".")),
                        "total_price": float(columns_values[4].replace(".", "").replace(",", ".")),
                    }
                )
                is_invoice_item_complete = True
                # print(f"3.6")
                continue
            if invoice_net_total_regx.match(row):
                net_total_amount = float(invoice_net_total_regx.findall(row)[0].replace(".", "").replace(",", "."))
                data_table_complete = True
                # print(f"net_total_amount-data_table_complete")
                continue
        if data_table_complete:
            if invoice_net_total_regx.match(row):
                net_total_amount = float(invoice_net_total_regx.findall(row)[0].replace(".", "").replace(",", "."))
                # print(f"net_total_amount")
                continue
            if vat_amount_regx.match(row):
                vat_amount = float(vat_amount_regx.findall(row)[0].replace(".", "").replace(",", "."))
                # print(f"vat_amount")
                continue
            if invoice_total_regx.match(row):
                total_amount = float(invoice_total_regx.findall(row)[0].replace(".", "").replace(",", "."))
                # print(f"total_amount")
            if is_file_totaled:
                invoice_reimbursement_notes.append(row)
                # print(f"parser: invoice_reimbursement_notes: {invoice_reimbursement_notes}")
    if data_table_complete and is_file_totaled:
        table_rows_df = pd.DataFrame(table_rows)
        print(f"table complete. num rows: {len(table_rows_df)}, df: {table_rows_df.to_string()}")
        data_sum_of_total = table_rows_df["total_price"].sum()
        notes = [
            note
            for note in invoice_reimbursement_notes
            if (not re.match("^Vielen Dank", note)) and (not re.match("^.*DE312095153", note))
        ]
        if not math.isclose(data_sum_of_total, net_total_amount, rel_tol=0.5):
            warnings.warn(
                f"Sum of invoice items not equal to total in file: {file_name}. "
                f"VAT amount: {vat_amount}, Net total: {net_total_amount}, Invoice total: {total_amount}, "
                f"Sum of invoice column 'total_price': {data_sum_of_total}. "
                f"Difference in net total: {net_total_amount - data_sum_of_total}, "
                f"Difference in total: {total_amount - data_sum_of_total}, "
                # f"table_rows_df: {table_rows_df.to_string()}"
            )
        if not math.isclose((vat_amount + net_total_amount), total_amount, rel_tol=0.5):
            warnings.warn(
                f"Sum of VAT and net total not equal to total in file: {file_name}. "
                f"VAT amount: {vat_amount}, Net total: {net_total_amount}, Invoice total: {total_amount}, "
                f"Sum of invoice table 'total' column: {data_sum_of_total}. "
                f"Difference in invoice VAT addition: {total_amount - (vat_amount + net_total_amount)}"
            )
        return {
            "date": invoice_reimbursement_date,
            "net_total": net_total_amount,
            "vat_amount": vat_amount,
            "total": total_amount,
            "table_data": table_rows_df,
            "notes": " ".join(notes),
            "extracted_metadata": extracted_metadata,
        }
    else:
        warnings.warn(
            f"Either empty PDF or something wrong during parsing: file: {file_name}, "
            f"data_table_complete: {data_table_complete}, "
            f"is_file_totaled: {is_file_totaled}"
        )
        return {
            "date": invoice_reimbursement_date,
            "net_total": net_total_amount,
            "vat_amount": vat_amount,
            "total": total_amount,
            "table_data": pd.DataFrame(),
            "notes": "",
            "extracted_metadata": extracted_metadata,
        }


def consolidate_extracted_data_into_df(extracted_data: dict, file_metadata: dict, file_name: str):
    table_data = extracted_data["table_data"]
    table_data["filename"] = file_name
    table_data["file_type"] = file_metadata["type"]
    table_data["date_filename"] = file_metadata["date_filename"]
    table_data["date"] = extracted_data["date"]
    table_data["net_total"] = extracted_data["net_total"]
    table_data["vat_amount"] = extracted_data["vat_amount"]
    table_data["total"] = extracted_data["total"]
    table_data["notes"] = extracted_data["notes"]
    table_data["invoice_or_reimbursement_nr_from_filename"] = file_metadata["invoice_reimbursement_nr"]
    table_data["order_nr_from_filename"] = file_metadata["order_nr"]
    table_data["invoice_nr_from_pdf"] = extracted_data["extracted_metadata"]["invoice_nr_from_pdf"]
    table_data["order_nr_from_pdf"] = extracted_data["extracted_metadata"]["order_nr_from_pdf"]
    table_data["reimbursement_nr_from_pdf"] = extracted_data["extracted_metadata"]["reimbursement_nr_from_pdf"]
    return table_data


def parse_monthly_pdfs_in_folder(folder_name: str, list_of_files: list):
    Path(os.path.join(os.getcwd(), "data/external_invoices/", folder_name)).mkdir(parents=True, exist_ok=True)
    invoice_tables_list = []
    for file_name in list_of_files:
        if ".pdf" in file_name.lower():
            pdf_path = os.path.join(INVOICES_DIR, folder_name, file_name)
            file_metadata = parse_invoice_reimbursement_info_from_filename(folder_name, file_name)
            pdf_text_lines = extract_text_from_pdfs(pdf_path)
            extracted_data = get_invoice_reimbursement_table_from_extracted_text(
                file_name,
                pdf_text_lines,
            )
            table_data = consolidate_extracted_data_into_df(extracted_data, file_metadata, file_name)
            invoice_tables_list.append(table_data)
        else:
            print(f"Not parsing non PDF file: {filename}")
    # combine all DFs and save as CSV
    if len(invoice_tables_list) > 0:
        combined_data = pd.concat(invoice_tables_list)
        if not combined_data.empty:
            combined_data.to_csv(
                path_or_buf=os.path.join(
                    os.getcwd(),
                    "data/external_invoices/",
                    folder_name,
                    "combined_data.csv",
                ),
                index=False,
            )
    else:
        warnings.warn(f"No files found to parse data. folder_name: {folder_name}")


if __name__ == "__main__":
    folders_metadata = parse_external_invoices_folder()
    print(f"folders_metadata.keys: {folders_metadata.keys()}")

    for folder_identifier, folder_metadata in folders_metadata.items():
        print(f"folder: {folder_identifier}, folder_metadata.keys: {folder_metadata.keys()}")
        if folder_identifier:
            if "RE" in folder_identifier or "GS" in folder_identifier:
                parse_monthly_pdfs_in_folder(folder_identifier, folder_metadata["files"])
            else:
                for filename in folder_metadata["files"]:
                    if ".xl" in filename.lower():
                        pass
                        # TODO: read file
                    elif ".csv" in filename.lower():
                        pass
                        # TODO: read file

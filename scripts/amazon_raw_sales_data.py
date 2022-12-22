import os

import pandas as pd

import logging
import dateparser
import datetime

# TODO: add data parallelisation.
# from multiprocessing import Pool
# pool = Pool()

from constants import AMAZON_SALES_DATA_DIR, COUNTRY_TO_COLUMNS_MAPPING
from utils.common import create_int_hash_from_df_row

logger = logging.getLogger()


def parse_sales_data_from_amazon_csvs() -> dict:
    all_amazon_sales_folders = [i[0] for i in os.walk(AMAZON_SALES_DATA_DIR)]
    sales_data = {}
    for folder_path in all_amazon_sales_folders:
        # all CSVs in folder for each country
        country_code = folder_path.split("/")[-1]

        if len(country_code) != 2 or ".DS_Store" in folder_path:
            logging.warning(
                f"Not a valid country folder, not parsing. folder path: {folder_path}"
            )
            continue

        country_sales_data = {}
        country_sales_data["files"] = {}

        logger.info(f"Parsing CSVs for country: {country_code} in: {folder_path}")

        csv_files_count = 0
        for country_filename in os.listdir(folder_path):
            if ".DS_Store" in country_filename:
                continue
            logger.info(f"\tFile: {country_filename}")

            data = pd.read_csv(
                os.path.join(AMAZON_SALES_DATA_DIR, folder_path, country_filename),
                skiprows=7,
                low_memory=False,
            )
            data = data[COUNTRY_TO_COLUMNS_MAPPING[country_code].keys()].copy()
            data.rename(columns=COUNTRY_TO_COLUMNS_MAPPING[country_code], inplace=True)
            data["country_code"] = country_code
            data["date_time"] = data["date_time_original"].apply(
                lambda date: dateparser.parse(date)
            )
            if country_code == "UK":
                data["currency"] = "GBP"
                data["total_price"] = (
                    data["total_price"]
                    .astype(str)
                    .str.replace(",", "", regex=False)
                    .astype(float)
                )
            elif country_code == "SE":
                data["currency"] = "SEK"
                data["total_price"] = (
                    data["total_price"]
                    .str.replace(".", "", regex=False)
                    .str.replace("\xa0", "", regex=False)
                    .str.replace(",", ".", regex=False)
                    .str.replace("−", "-", regex=False)
                    .astype(float)
                )
            elif country_code == "PL":
                data["currency"] = "PLN"
                data["total_price"] = (
                    data["total_price"]
                    .str.replace(".", "", regex=False)
                    .str.replace(",", ".", regex=False)
                    .astype(float)
                )
            else:
                data["currency"] = "EUR"
                data["total_price"] = (
                    data["total_price"]
                    .str.replace(".", "", regex=False)
                    .str.replace(",", ".", regex=False)
                    .str.replace("\u202f", "", regex=False)
                    .str.replace("−", "-", regex=False)
                    .astype(float)
                )
            assert (
                data["date_time_original"].count() == data["date_time"].count()
            ), f"Could not convert all dates for: {country_code}."

            country_sales_data["files"][country_filename] = data
            csv_files_count += 1
        country_sales_data["csv_count"] = csv_files_count
        sales_data[country_code] = country_sales_data

    all_data = {}
    for country_code in sales_data.keys():
        if sales_data[country_code]["csv_count"] != len(
            sales_data[country_code]["files"]
        ):
            raise Exception(
                f"Number of files does not match csv_count. country: {country_code}"
                f"""number of files: {sales_data[country_code]["files"]}"""
                f"""csv_count: {sales_data[country_code]["csv_count"]}"""
            )
        yearly_data = []
        monthly_data = []
        yearly_data_df = None
        monthly_data_df = None
        row_counts = 0
        for file, data in sales_data[country_code]["files"].items():
            rows = len(data)
            if rows > 0:
                data["source_file"] = file
                if "monthly" in file.lower():
                    monthly_data.append(data)
                else:
                    yearly_data.append(data)
                row_counts += rows
            else:
                logging.warning(f"Skipping file: {file}. Empty file {rows} rows.")

        if len(yearly_data) < 1 and len(monthly_data) < 1:
            logging.warning(
                f"cannot create DF, skipping processing for country_code: {country_code}. "
                "Empty yearly and monthly data."
            )
            continue
        else:
            yearly_data_df = pd.concat(yearly_data) if yearly_data else pd.DataFrame()
            monthly_data_df = (
                pd.concat(monthly_data) if monthly_data else pd.DataFrame()
            )

        total_data_count = len(yearly_data_df) + len(monthly_data_df)
        if row_counts != total_data_count:
            raise Exception(
                f"Total records count does not match."
                f"Sum of individual data files: {row_counts}"
                f"Sum of yearly and monthly data: {total_data_count}"
            )

        all_data[country_code] = {
            "all_data": pd.concat([yearly_data_df, monthly_data_df]),
            "row_count": row_counts,
        }

    return all_data


if __name__ == "__main__":
    needed_columns = [
        "hash_id",
        "date_time_original",
        "date_time",
        "settlement_id",
        "type",
        "order_id",
        "sku",
        "quantity",
        "total_price",
        "marketplace",
        "fulfilment",
        "source_file",
        "country_code",
    ]
    country_combined_sales_data = parse_sales_data_from_amazon_csvs()

    # save combined data to sales data directory
    current_date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"all_sales_data_combined_{current_date}.csv"
    all_global_data_list = []
    for country, data in country_combined_sales_data.items():
        all_global_data_list.append(data["all_data"])
    all_global_data_df = pd.concat(all_global_data_list, ignore_index=True)

    logger.info(f"Final DF column counts: {all_global_data_df.count()}")

    all_global_data_df["hash_id"] = all_global_data_df.apply(
        lambda row: create_int_hash_from_df_row(row), axis=1
    )
    output_csv_path = os.path.join(os.getcwd(), "data", "amazon_sales", filename)
    logger.info(f"Saving file to: {output_csv_path}")
    all_global_data_df[needed_columns].to_csv(
        path_or_buf=output_csv_path,
        index=False,
    )

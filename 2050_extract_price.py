import pandas as pd
from pathlib import Path
from types import SimpleNamespace
from config_reader import ConfigReader
from dancik_uom import UOMService
from query_loader import QueryLoader
from database import Database


def get_basic_uom(row):
    if row["ICOMPO"] == 'R':
        return "LF"
    else:
        if row["IUM2"] is None:
            return row["IUNITS"].strip()
        else:
            return f"{row["IUM2"].strip()}"



def get_sales_uom(row):
    if get_basic_uom(row) == "CT":
        return "SF"
    return row["IUNITS"].strip()

def main():

    config = ConfigReader.get_instance()
    prefix = input(
        "Enter the prefix used for the price query: "
    ).strip().replace(" ", "_") or ""

    # if prefix is not empty, ensure it ends with an underscore
    if prefix and not prefix.endswith("_"):
        prefix += "_"

    query = QueryLoader.load_query(f"{prefix}dancik_price_extraction_query")

    with Database() as db:
        df = db.fetch_dataframe(query)

    print("Available columns:", df.columns.tolist())

    for _, row in df.iterrows():
        item_number = row["ITEMNUMBER"]
        uom_service = UOMService(item_number)

        row["sales_price"] = uom_service.convert_price(row["LIST"], row["IUNITS"], get_sales_uom(row))

        print(f"Processed item: {item_number}, {row["LIST"]} / IUNITS: {row['IUNITS']}, Sales Price: {row['sales_price']} per {get_sales_uom(row)}")

    print(f"Fetched {len(df)} rows from the database.")


if __name__ == "__main__":
    main()
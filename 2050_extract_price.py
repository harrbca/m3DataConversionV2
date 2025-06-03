import pandas as pd
from pathlib import Path
from types import SimpleNamespace
from config_reader import ConfigReader
from dancik_uom import UOMService
from query_loader import QueryLoader
from database import Database
from template_helper import TemplateHelper
from transformer_factory import TransformerFactory


def get_basic_uom(row):
    if row["ICOMPO"] == 'R':
        return "LF"
    else:
        if row["IUM2"] is None:
            return row["IUNITS"].strip()
        else:
            return row["IUM2"].strip()



def get_sales_uom(row):
    if get_basic_uom(row) == "CT":
        return "SF"
    return row["IUNITS"].strip()

def main():

    config = ConfigReader.get_instance()
    prefix = input(
        "Enter the prefix used for the price query: "
    ).strip().replace(" ", "_") or ""

    valid_from_date = input(
        "Enter the valid from date (YYYYMMDD): "
    ).strip()

    price_list_name = input(
        "Enter the price list name: "
    ).strip()

    price_list_currency = input(
        "Enter the price list currency: "
    ).strip()

    # if prefix is not empty, ensure it ends with an underscore
    if prefix and not prefix.endswith("_"):
        prefix += "_"

    query = QueryLoader.load_query(f"{prefix}dancik_price_extraction_query")

    with Database() as db:
        df = db.fetch_dataframe(query)

    df.columns = df.columns.str.upper()

    print("Available columns:", df.columns.tolist())

    # 7) Initialize TransformerFactory (using document_mappings.yml)
    mapper_path = Path("config") / "document_mappings.yml"
    factory = TransformerFactory(str(mapper_path))

    # load the template for the output
    template_helper = TemplateHelper("API_OIS017MI_AddBasePrice.xlsx")

    for _, row in df.iterrows():
        try:
            item_number = row["ITEMNUMBER"]
            uom_service = UOMService(item_number)

            row["sales_price"] = uom_service.convert_price(row["LIST"], row["IUNITS"], get_sales_uom(row), 2)
            row["valid_from"] = valid_from_date
            row["price_list_name"] = price_list_name
            row["price_list_currency"] = price_list_currency

            transformed = factory.transform_row("API_OIS017MI_AddBasePrice", row)
            if transformed:
                template_helper.add_row(transformed)

            print(f"Processed item: {item_number}, {row["LIST"]} / IUNITS: {row['IUNITS']}, Sales Price: {row['sales_price']} per {get_sales_uom(row)}")
        except Exception as e:
            print(f"Error processing item {row['ITEMNUMBER']}: {e}")
            continue

    print(f"Fetched {len(df)} rows from the database.")
    template_helper.save("ois017_output_path")


if __name__ == "__main__":
    main()
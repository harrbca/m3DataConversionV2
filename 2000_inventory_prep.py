from ftplib import error_perm

import pandas as pd

from dancik_uom import UOMService
from database import Database
from query_loader import QueryLoader
from path_manager import PathManager


def get_basic_uom(row):
    if getattr(row, 'ICOMPO', '') == 'R':
        return "LF"
    else:
        if getattr(row, 'IUM2') is None:
            return getattr(row, 'IUNITS', '').strip()
        else:
            return getattr(row, 'IUM2', '').strip()

def export_inventory_to_excel():
    # Ask user for a prefix
    prefix = input("Enter export file suffix: ").strip().replace(" ", "_") or "export"

    # Load SQL query
    sql_query = QueryLoader.load_query("bwl_inventory_query")

    # Resolve output path using PathManager
    path_manager = PathManager()
    output_path = path_manager.get_path("PATHS", "inventory_export_path", suffix=prefix)


    # Fetch data
    with Database() as db:
        df = db.fetch_dataframe(sql_query)

    converted_rows = []
    error_rows = []

    for _, row in df.iterrows():
        item_number = row["itemNumber"]
        rum = row["RUM"]
        cost = row["RLASTC"]
        onhand = row["RONHAN"]
        cost_uom = row["IUNITC"]
        basic_uom = get_basic_uom(row)

        uom_service = UOMService(item_number)

        if cost_uom == "CT" and uom_service.has_uom("SF"):
            cost_uom = "SF"


        if cost_uom and rum and onhand is not None:
            try:
                converted_qty = uom_service.convert(onhand, rum, cost_uom)
                converted_cost = uom_service.convert_price(cost, rum, cost_uom)
                basic_uom_qty = uom_service.convert(onhand, rum, basic_uom)
                row["RONHAN"] = converted_qty
                row["RUM"] = cost_uom
                row["RLASTC"] = converted_cost
                row["basic_uom"] = basic_uom
                row["basic_uom_qty"] = basic_uom_qty
                converted_rows.append(row)
            except Exception as e:
                print(f"Error converting UOM for item {item_number}: {e}")
                row["onhand_converted"] = onhand
                row["cost_uom"] = rum
                row["cost_converted"] = cost
                error_rows.append(row)
        else:
            row["onhand_converted"] = onhand
            row["cost_uom"] = rum
            row["cost_converted"] = cost
            error_rows.append(row)



    # Save to Excel
    output_df = pd.DataFrame(converted_rows)
    output_df.to_excel(output_path, index=False, engine="openpyxl")
    print(f"✅ Exported {len(output_df)} rows to {output_path}")

    if error_rows:
        error_df = pd.DataFrame(error_rows)
        error_path = path_manager.get_path("PATHS", "inventory_export_path", suffix="error")
        error_df.to_excel(error_path, index=False, engine="openpyxl")
        print(f"⚠️ Exported {len(error_rows)} rows with errors to {error_path}")



if __name__ == "__main__":
    export_inventory_to_excel()

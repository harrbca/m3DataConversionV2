import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed
from decimal import Decimal
from dancik_uom import UOMService
from database import Database
from query_loader import QueryLoader
from path_manager import PathManager


def process_row(row_dict):
    try:
        item_number = row_dict["itemNumber"]
        rum = row_dict["RUM"]
        cost = row_dict["RLASTC"]
        onhand = row_dict["RONHAN"]
        cost_uom = row_dict["IUNITC"]
        uom_service = UOMService(item_number)

        if cost_uom == "CT" and uom_service.has_uom("SF"):
            cost_uom = "SF"

        if cost_uom and rum and onhand is not None:
            converted_qty = uom_service.convert(onhand, rum, cost_uom)
            converted_cost = uom_service.convert_price(cost, rum, cost_uom)

            row_dict["RONHAN"] = converted_qty
            row_dict["RUM"] = cost_uom
            row_dict["RLASTC"] = converted_cost
            row_dict["error"] = None
        else:
            row_dict["onhand_converted"] = onhand
            row_dict["cost_uom"] = rum
            row_dict["cost_converted"] = cost
            row_dict["error"] = "Missing UOM or onhand"

    except Exception as e:
        row_dict["onhand_converted"] = onhand
        row_dict["cost_uom"] = rum
        row_dict["cost_converted"] = cost
        row_dict["error"] = f"Error: {e}"

    return row_dict


def export_inventory_to_excel_parallel():
    prefix = input("Enter export file suffix: ").strip().replace(" ", "_") or "export"
    sql_query = QueryLoader.load_query("bwl_inventory_query")
    path_manager = PathManager()
    output_path = path_manager.get_path("PATHS", "inventory_export_path", suffix=prefix)

    with Database() as db:
        df = db.fetch_dataframe(sql_query)

    rows = df.to_dict(orient="records")
    results = []

    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(process_row, row) for row in rows]

        for future in as_completed(futures):
            results.append(future.result())

    # Separate success and error rows
    converted_rows = [r for r in results if r.get("error") is None]
    error_rows = [r for r in results if r.get("error") is not None]

    pd.DataFrame(converted_rows).to_excel(output_path, index=False, engine="openpyxl")
    print(f"✅ Exported {len(converted_rows)} rows to {output_path}")

    if error_rows:
        error_path = path_manager.get_path("PATHS", "inventory_export_path", suffix="error")
        pd.DataFrame(error_rows).to_excel(error_path, index=False, engine="openpyxl")
        print(f"⚠️ Exported {len(error_rows)} rows with errors to {error_path}")


if __name__ == "__main__":
    export_inventory_to_excel_parallel()

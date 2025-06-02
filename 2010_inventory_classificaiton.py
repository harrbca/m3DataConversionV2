import pandas as pd
from database import Database
from path_manager import PathManager
from config_reader import ConfigReader

# === ItemType → Category Mapping ===
ITEMTYPE_CATEGORY_MAP = {
    "BAS": "Average Costed",
    "DIS": "Average Costed",
    "HPL": "Average Costed",
    "IMA": "Average Costed",
    "MOL": "Average Costed",
    "PAD": "Average Costed",
    "RUB": "Average Costed",
    "SAM": "Average Costed",
    "CAR": "Roll Goods",
    "RES": "Roll Goods",
    "VCT": "Shade Controlled",
}

# === Main Function ===
def classify_inventory():
    # Prompt for suffix
    suffix = input("Enter input/output file suffix: ").strip().replace(" ", "_") or "export"

    config = ConfigReader.get_instance()
    path_manager = PathManager()

    # Resolve input/output paths with suffix
    input_path = path_manager.get_path("PATHS", "inventory_export_path", suffix=suffix, check_path=False)
    output_path = path_manager.get_path("PATHS", "inventory_classified_path", suffix=suffix)


    # Read input spreadsheet
    df = pd.read_excel(input_path, engine="openpyxl")

    # Prepare category buckets
    categories = {
        "Average Costed": [],
        "Roll Goods": [],
        "Shade Controlled": [],
        "Non Lot Controlled": []
    }

    with Database() as db:
        for _, row in df.iterrows():
            item_number = row["itemNumber"]

            try:
                result = db.execute(
                    "SELECT ItemType FROM item_hierarchy WHERE H_ITEMNUMBER = ?",
                    (item_number,)
                ).fetchone()
                item_type = result["ItemType"] if result else None
            except Exception as e:
                print(f"⚠️ DB error for item {item_number}: {e}")
                item_type = None

            category = ITEMTYPE_CATEGORY_MAP.get(item_type, "Non Lot Controlled")
            categories[category].append(row)

        # Save to Excel with 4 sorted sheets
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            for sheet, rows in categories.items():
                if rows:
                    df_sheet = pd.DataFrame(rows)
                    df_sheet = df_sheet.sort_values(
                        by=["RWARE#", "itemNumber", "RROLL#", "RLOC1", "RLRCTD"],
                        na_position="last"
                    )
                    df_sheet.to_excel(writer, sheet_name=sheet, index=False)

    print(f"✅ Classified inventory saved to: {output_path}")


if __name__ == "__main__":
    classify_inventory()

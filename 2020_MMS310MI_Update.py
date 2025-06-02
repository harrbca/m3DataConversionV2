import pandas as pd
from pathlib import Path
from types import SimpleNamespace
from config_reader import ConfigReader
from transformer_factory import TransformerFactory
from template_helper import TemplateHelper
from path_manager import PathManager

class RowWrapper:
    """
    Wraps a pandas Series so that getattr(wrapper, "COLNAME") returns series["COLNAME"].
    This lets us keep column names like "RWARE#" and "LOT#" without renaming them.
    """
    def __init__(self, series: pd.Series):
        self._series = series

    def __getattr__(self, name: str):
        # If the series has a column exactly matching 'name', return it (or empty string)
        if name in self._series:
            val = self._series[name]
            # If it's NaN, convert to empty string
            return "" if pd.isna(val) else val
        # Otherwise, fallback
        raise AttributeError(f"{name!r} not found in row")

def cyy_to_yyyymmdd(cyy_str: str) -> str:
    """
    Convert a CYYMMDD string (e.g. "1241002") to "YYYYMMDD" (e.g. "20241002").
    C = century digit (0 → 1900s, 1 → 2000s), YY = year, MM = month, DD = day.
    If the input isn’t exactly 7 digits or non‐numeric, returns an empty string.
    """
    s = (cyy_str or "").strip()
    if len(s) != 7 or not s.isdigit():
        return ""
    c  = int(s[0])
    yy = int(s[1:3])
    mm = s[3:5]
    dd = s[5:7]
    year = 1900 + yy + (c * 100)
    return f"{year:04d}{mm}{dd}"

def main():
    # 1) Load config and ask for the suffix
    config = ConfigReader.get_instance()
    suffix = input(
        "Enter the suffix used for the classified inventory file: "
    ).strip().replace(" ", "_") or "classified"

    # 2) Resolve the path to your classified‐inventory spreadsheet
    path_manager = PathManager()
    classified_path = path_manager.get_path("PATHS", "inventory_classified_path", suffix=suffix, check_path=False)
    if not classified_path.exists():
        print(f"❌ Classified‐inventory file not found at: {classified_path}")
        return

    print(f"🔍 Loading classified inventory from: {classified_path}")

    # 3) Read only the three sheets: Roll Goods, Shade Controlled, Non Lot Controlled
    sheets_to_process = {"Roll Goods", "Shade Controlled", "Non Lot Controlled"}
    dfs = []
    with pd.ExcelFile(classified_path, engine="openpyxl") as xls:
        for sheet_name in xls.sheet_names:
            if sheet_name not in sheets_to_process:
                continue

            df_sheet = pd.read_excel(
                xls,
                sheet_name=sheet_name,
                engine="openpyxl",
                dtype=str
            )

            # 3b) Convert RLRCTD from CYYMMDD → YYYYMMDD
            df_sheet["RLRCTD"] = (
                df_sheet["RLRCTD"].fillna("").astype(str).apply(cyy_to_yyyymmdd)
            )

            # 3c) Drop rows missing itemNumber, RWARE#, or LOT#
            df_sheet = df_sheet.dropna(subset=["itemNumber", "RWARE#", "LOT#"])
            df_sheet = df_sheet[df_sheet["LOT#"].str.strip() != ""]

            dfs.append(df_sheet)

    if not dfs:
        print("❌ No valid sheets (Roll Goods/​Shade Controlled/​Non Lot Controlled) found.")
        return

    # 4) Concatenate
    df = pd.concat(dfs, ignore_index=True)


    # 7) Initialize TransformerFactory (using document_mappings.yml)
    mapper_path = Path("config") / "document_mappings.yml"
    factory = TransformerFactory(str(mapper_path))

    # 8) Load the “API_MMS310_Update.xlsx” template
    template_name = "API_MMS310MI_Update.xlsx"
    template_helper = TemplateHelper(template_name)
    print(f"   • Loaded template: {template_name}")



    # 9) Iterate over each unique row using iterrows() + RowWrapper (no itertuples)
    for _, series in df.iterrows():
        row_obj = RowWrapper(series)

        transformed = factory.transform_row("API_MMS310MI_Update", row_obj)
        if transformed:
            template_helper.add_row(transformed)

    # 10) Save the filled‐in template to the path defined by “mms235_output_path”
    template_helper.save("mms310_output_path")
    print("✅ API_MMS310MI_Update spreadsheet has been created.")



if __name__ == "__main__":
    main()

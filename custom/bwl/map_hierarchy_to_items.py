import pandas as pd
import numpy as np
import sqlite3
from joblib import Parallel, delayed
import matplotlib.pyplot as plt
import time
from collections import Counter

# Globals
_global_df = None
_pc_cols = None

def set_globals(df):
    global _global_df, _pc_cols
    _global_df = df.copy()
    _global_df.replace(np.nan, "", inplace=True)

    # Ensure PL1, PL2 are treated as strings
    for col in ["PL1", "PL2"]:
        if col in _global_df.columns:
            _global_df[col] = _global_df[col].astype(str).str.strip()

    _pc_cols = [c for c in _global_df.columns if c.startswith("PC")]

def vectorized_match(item, weights=None):
    global _global_df, _pc_cols

    if weights is None:
        weights = {
            "price_class":   5,
            "product_line":  4,
            "item_class2":   3,
            "item_class1":   2,
            "manufacturer":  1
        }

    product_line = item["IPRODL"].strip()
    manufacturer = item["IMFGR"].strip()
    item_class1 = item["ICLAS1"].strip()
    item_class2 = item["ICLAS2"].strip()
    price_class = item["IPRCCD"].strip()

    # 🆕 Early return for sample items
    if product_line in {"SAM", "SET"}:
        return {
            "ITEMNUMBER": item["ITEMNUMBER"],
            "INAME": item["INAME"],
            "INAME2": item["INAME2"],
            "MFGR": item["IMFGR"],
            "PRODUCTLINE": product_line,
            "ITEMCLASS1": item["ICLAS1"].strip(),
            "ITEMCLASS2": item["ICLAS2"].strip(),
            "PRICECLASS": item["IPRCCD"].strip(),
            "ItemType": "SAM",
            "H1": "SAM",
            "H2": None,
            "H3": None,
            "H4": None,
            "H1Desc": "SAMPLE",
            "H2Desc": None,
            "H3Desc": None,
            "H4Desc": None,
            "Score": 0,
            "MatchedFields": "SAMPLE_OVERRIDE"
        }

    df = _global_df

    # ❗ Filter out any rows where price_class matches OPC1 to OPC4
    omit_cols = [col for col in df.columns if col.startswith("OPC")]
    if omit_cols:
        omit_mask = df[omit_cols].eq(price_class).any(axis=1)
        df = df[~omit_mask]  # Keep only non-matching rows

    feature_hits = {
        "price_class": df[_pc_cols].eq(price_class).any(axis=1),
        "product_line": df[["PL1", "PL2"]].eq(product_line).any(axis=1),
        "item_class2": (df["IC2"] == item_class2) & (item_class2 != ""),
        "item_class1": df["IC1"] == item_class1,
        "manufacturer": df["MFGR"] == manufacturer,
    }

    score = pd.Series(0, index=df.index)
    for key, mask in feature_hits.items():
        score += mask.astype(int) * weights[key]

    max_idx = score.idxmax()
    max_score = score[max_idx]

    result = {
        "ITEMNUMBER": item["ITEMNUMBER"],
        "INAME": item["INAME"],
        "INAME2": item["INAME2"],
        "MFGR": item["IMFGR"],
        "PRODUCTLINE": product_line,
        "ITEMCLASS1": item_class1,
        "ITEMCLASS2": item_class2,
        "PRICECLASS": price_class,
        "Score": int(max_score)
    }

    if max_score > 0:
        best_row = df.loc[max_idx]
        result.update({
            "ItemType": best_row["ItemType"],
            "H1": best_row["H1"],
            "H2": best_row["H2"],
            "H3": best_row["H3"],
            "H4": best_row["H4"],
            "H1Desc": best_row["H1Desc"],
            "H2Desc": best_row["H2Desc"],
            "H3Desc": best_row["H3Desc"],
            "H4Desc": best_row["H4Desc"]
        })
        result["MatchedFields"] = ", ".join([k for k, v in feature_hits.items() if v[max_idx]])
    else:
        result.update({k: None for k in ["ItemType", "H1", "H2", "H3", "H4", "H1Desc", "H2Desc", "H3Desc", "H4Desc"]})
        result["MatchedFields"] = ""

    return result

def print_text_histogram(score_counts, max_width=40):
    max_count = score_counts.max()
    print("\n📊 Match Score Histogram (console):")
    for score, count in score_counts.items():
        bar_len = int(count / max_count * max_width)
        bar = "█" * bar_len
        print(f"Score {score:>2}: {bar} ({count})")

if __name__ == '__main__':
    start = time.time()

    print("🔄 Loading spreadsheet...")
    df = pd.read_excel("c:\\infor_migration\\spreadsheets\\BWL_WANKE_COMBINED_H3.xlsx")
    set_globals(df)

    print("🔄 Connecting to database...")
    conn = sqlite3.connect(r"c:\\infor_migration\\db\\migration.db")
    cursor = conn.cursor()
    rows = cursor.execute("SELECT * FROM dancik_items ORDER BY itemnumber").fetchall()
    col_names = [desc[0].upper() for desc in cursor.description]
    items = [dict(zip(col_names, row)) for row in rows]
    conn.close()

    print(f"📦 Loaded {len(items)} items. Matching...")

    results = Parallel(n_jobs=-1, backend="loky", batch_size=100)(
        delayed(vectorized_match)(item) for item in items
    )

    results_df = pd.DataFrame(results)
    output_excel = "c:\\infor_migration\\spreadsheets\\map_hierarchy_to_items17.xlsx"
    results_df.to_excel(output_excel, index=False)
    print(f"📄 Excel written to: {output_excel}")



    print(f"\n✅ Done in {time.time() - start:.2f} seconds")
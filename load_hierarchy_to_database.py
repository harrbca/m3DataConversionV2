from database import Database
import pandas as pd

EXCEL_PATH = r"c:\infor_migration\spreadsheets\map_hierarchy_to_items17.xlsx"
TABLE_NAME = "item_hierarchy"
MONITORED_FIELDS = ["H1", "H2", "H3", "H4", "ItemType"]

def ensure_table_exists(db):
    db.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            H_ITEMNUMBER TEXT PRIMARY KEY,
            H1 TEXT, H2 TEXT, H3 TEXT, H4 TEXT,
            H1Desc TEXT, H2Desc TEXT, H3Desc TEXT, H4Desc TEXT,
            ItemType TEXT,
            LastUpdated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

def get_existing_data(db):
    def normalize(value):
        if value is None:
            return None
        if isinstance(value, str):
            return value.strip()
        return value

    rows = db.execute(f"SELECT * FROM {TABLE_NAME}").fetchall()

    return {
        row["H_ITEMNUMBER"]: {k: normalize(row[k]) for k in MONITORED_FIELDS}
        for row in rows
    }

def upsert_data(db, df, update_mode):
    existing = get_existing_data(db)
    changes = []

    for _, row in df.iterrows():
        item_id = row["H_ITEMNUMBER"]
        row_data = {k: row[k] for k in MONITORED_FIELDS}

        if item_id not in existing:
            if update_mode:
                db.execute(f"""
                    INSERT INTO {TABLE_NAME} (H_ITEMNUMBER, H1, H2, H3, H4, H1Desc, H2Desc, H3Desc, H4Desc, ItemType)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item_id,
                    row["H1"], row["H2"], row["H3"], row["H4"],
                    row["H1Desc"], row["H2Desc"], row["H3Desc"], row["H4Desc"],
                    row["ItemType"]
                ))
            print(f"➕ New item to insert: {item_id}")
        else:
            old = existing[item_id]
            diff = {
                k: (old[k], row[k])
                for k in MONITORED_FIELDS
                if as_clean_str(old[k]) != as_clean_str(row[k])
            }

            if diff:
                if update_mode:
                    db.execute(f"""
                        UPDATE {TABLE_NAME}
                        SET H1=?, H2=?, H3=?, H4=?, H1Desc=?, H2Desc=?, H3Desc=?, H4Desc=?, ItemType=?, LastUpdated=CURRENT_TIMESTAMP
                        WHERE H_ITEMNUMBER=?
                    """, (
                        row["H1"], row["H2"], row["H3"], row["H4"],
                        row["H1Desc"], row["H2Desc"], row["H3Desc"], row["H4Desc"],
                        row["ItemType"], item_id
                    ))
                changes.append(
                    f"🔄 Changes for {item_id}:\n" +
                    "\n".join(f"  - {field}: '{old[field]}' → '{row[field]}'" for field in diff)
                )

    if changes:
        print("\n📝 Change Log:")
        for line in changes:
            print(line)
    else:
        print("✅ No updates required.")

def as_clean_str(val):
    if val is None:
        return ""
    return str(val).strip()

def prompt_mode():
    while True:
        mode = input("⚙️ Run in TEST mode or UPDATE mode? [T/U]: ").strip().lower()
        if mode in ['t', 'u']:
            return mode == 'u'
        print("❗ Please enter 'T' for test or 'U' for update.")

def main():
    update_mode = prompt_mode()
    df = pd.read_excel(EXCEL_PATH)
    df = df.rename(columns={"ITEMNUMBER": "H_ITEMNUMBER"})
    df = df.where(pd.notnull(df), None)  # Replace NaN with None
    df = df.applymap(lambda x: str(x).strip() if isinstance(x, str) else x)  # Strip strings

    with Database() as db:
        ensure_table_exists(db)
        upsert_data(db, df, update_mode)

    print("\n🎉 Done.")

if __name__ == "__main__":
    main()

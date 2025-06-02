import os
import sys
import argparse
import decimal
import sqlite3
import pandas as pd
import pyodbc
from config_reader import ConfigReader
from path_manager import PathManager

# Define all datasets in one place for easy extension
DATASETS = [
    {
        'key': 'items',
        'query_key': 'dancik_items_query',
        'table_key': 'dancik_items_table'
    },
    {
        'key': 'billto',
        'query_key': 'dancik_billto_query',
        'table_key': 'dancik_billto_table'
    },
    {
        'key': 'price',
        'query_key': 'dancik_price_query',
        'table_key': 'dancik_price_table'
    },
    {
        'key': 'rolls',
        'query_key': 'dancik_rolls_query',
        'table_key': 'dancik_rolls_table'
    },
    # Warehouse tables
    {
        'key': 'wm0002f',
        'query_key': 'dancik_wm0002f_query',
        'table_key': 'dancik_wm0002f_table'
    },
    {
        'key': 'wm0003f',
        'query_key': 'dancik_wm0003f_query',
        'table_key': 'dancik_wm0003f_table'
    },
    {
        'key': 'wm0005f',
        'query_key': 'dancik_wm0005f_query',
        'table_key': 'dancik_wm0005f_table'
    },
    {
        'key': 'wm0006f',
        'query_key': 'dancik_wm0006f_query',
        'table_key': 'dancik_wm0006f_table'
    }
]


def connect_source():
    """
    Establish a connection to the source database using ODBC.
    Credentials come from the [CONNECTION] section of config.ini.
    """
    config = ConfigReader.get_instance()
    db_type = config.get_connection("DB_TYPE").lower()
    if db_type == "as400":
        host = config.get_connection("AS400_HOST")
        user = config.get_connection("AS400_USERNAME")
        pwd = config.get_connection("AS400_PASSWORD")
        conn_str = (
            f"DRIVER={{iSeries Access ODBC Driver}};"
            f"SYSTEM={host};UID={user};PWD={pwd};naming=1;READONLY=1;"
        )
    elif db_type in ("mssql", "sqlserver"):
        server = config.get_connection("DB_SERVER")
        database = config.get_connection("DB_DATABASE")
        user = config.get_connection("DB_USERNAME")
        pwd = config.get_connection("DB_PASSWORD")
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};DATABASE={database};UID={user};PWD={pwd};"
        )
    else:
        raise ValueError(f"Unsupported DB_TYPE: {db_type}")
    return pyodbc.connect(conn_str)


def fetch_data(query_path):
    """
    Execute the SQL query at query_path and return as a DataFrame.
    """
    print(f"Reading query from {query_path}")
    with open(query_path, "r") as f:
        sql = f.read()
    conn = connect_source()
    cursor = conn.cursor()
    print("Executing query...")
    cursor.execute(sql)
    cols = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    df = pd.DataFrame([tuple(r) for r in rows], columns=cols)
    return df


def save_to_sqlite(df, table, db_path, ask_confirm):
    """
    Save DataFrame to a SQLite table, optionally confirming per-table overwrite.
    Converts Decimal to str for compatibility.
    """
    # Convert decimals
    df = df.apply(lambda col: col.map(lambda x: float(x) if isinstance(x, decimal.Decimal) else x))

    # Ensure DB directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if table exists
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
        (table,)
    )
    exists = cursor.fetchone() is not None

    # Prompt if requested and table already exists
    if exists and ask_confirm:
        resp = input(f"⚠️ Table '{table}' exists in {db_path}. Overwrite? (y/n): ")
        if resp.lower() != 'y':
            print(f"Skipping load for table '{table}'.")
            conn.close()
            return

    # Write (will replace if_exists='replace')
    df.to_sql(table, conn, if_exists='replace', index=False)
    conn.close()
    print(f"✅ Loaded DataFrame into SQLite table '{table}'")


def interactive_menu(options):
    """
    Display a menu and return the chosen key, or None to exit.
    """
    print("\nSelect data set to load:")
    for i, opt in enumerate(options, start=1):
        print(f"  {i}. {opt}")
    print("  0. Exit")
    choice = input("Enter choice: ")
    if choice == '0':
        return None
    try:
        idx = int(choice) - 1
        return options[idx]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return interactive_menu(options)


def main():
    config = ConfigReader.get_instance()
    pm = PathManager()
    db_path = pm.get_path('PATHS', 'db_path')

    # Build list of available keys
    keys = [d['key'] for d in DATASETS]
    keys.append('all')

    parser = argparse.ArgumentParser(
        description='Load data from source DB into SQLite'
    )
    parser.add_argument('-l', '--load', choices=keys,
                        help='Which dataset to load')
    parser.add_argument('-c', '--confirm', action='store_true',
                        help='Ask before overwriting existing tables')
    args = parser.parse_args()

    # Determine mode: interactive or single-run
    if args.load:
        targets = keys[:-1] if args.load == 'all' else [args.load]
        for tgt in targets:
            ds = next(d for d in DATASETS if d['key'] == tgt)
            qpath = config.get('QUERIES', ds['query_key'])
            tbl   = config.get('DB', ds['table_key'])
            df    = fetch_data(qpath)
            save_to_sqlite(df, tbl, db_path, ask_confirm=args.confirm)
        print('✅ All tasks completed.')
        sys.exit(0)

        # Interactive loop
    while True:
        choice = interactive_menu(keys)
        if not choice:
            print('Exiting.')
            break
        if choice == 'all':
            for tgt in keys[:-1]:
                ds = next(d for d in DATASETS if d['key'] == tgt)
                qpath = config.get('QUERIES', ds['query_key'])
                tbl = config.get('DB', ds['table_key'])
                df = fetch_data(qpath)
                save_to_sqlite(df, tbl, db_path, ask_confirm=args.confirm)
            print('✅ All datasets loaded.')
            continue

        ds = next(d for d in DATASETS if d['key'] == choice)
        qpath = config.get('QUERIES', ds['query_key'])
        tbl = config.get('DB', ds['table_key'])
        df = fetch_data(qpath)
        save_to_sqlite(df, tbl, db_path, ask_confirm=args.confirm)

    print('Goodbye.')


if __name__ == '__main__':
    main()

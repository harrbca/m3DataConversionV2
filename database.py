import sqlite3
import pandas as pd
from config_reader import ConfigReader
from path_manager import PathManager

class Database:
    def __init__(self):
        config = ConfigReader.get_instance()
        path_manager = PathManager()
        self.db_path = path_manager.get_path("PATHS", "db_path")

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            self.conn.rollback()
        else:
            self.conn.commit()
        self.conn.close()

    def execute(self, query, params=None):
        if params is None:
            params = ()
        self.cursor.execute(query, params)
        return self.cursor

    def fetch_dataframe(self, query, params=None):
        """Execute a SQL query and return the results as a Pandas DataFrame."""
        if params is None:
            params = ()
        return pd.read_sql_query(query, self.conn, params=params)
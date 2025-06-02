from config_reader import ConfigReader
from pathlib import Path


class QueryLoader:
    @staticmethod
    def load_query(key: str, section: str = "QUERIES") -> str:
        """
        Load a SQL query from a file path defined in the config file.

        Args:
            key (str): The key in the config section pointing to the SQL file path.
            section (str): The section name in config.ini (default: "QUERIES").

        Returns:
            str: The contents of the SQL file.
        """
        config = ConfigReader.get_instance()
        path_str = config.get(section, key, fallback=None)
        if not path_str:
            raise ValueError(f"No path configured for [{section}] {key}")

        path = Path(path_str)
        if not path.exists():
            raise FileNotFoundError(f"SQL file does not exist: {path}")

        with open(path, "r") as f:
            return f.read()


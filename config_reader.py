import configparser
import os
import glob

class ConfigReader:
    _instance = None
    _credentials_missing = True

    def __init__(self, config_file=None, credentials_filename="credentials.ini"):
        if hasattr(self, "config"):
            return

        # 1) Find & load the main config.ini
        self.config_file = config_file or self._find_config_file()
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)

        # 2) Compute where the credentials file lives
        #    First, look for a base_path key in DEFAULT
        base_path = self.config.get("DEFAULT", "base_path", fallback=None)

        #    If it’s there, use it; otherwise fall back to a relative path
        if base_path:
            self.credentials_file = os.path.join(base_path, credentials_filename)
        else:
            # assume credentials live next to your config directory:
            config_dir = os.path.dirname(self.config_file)
            self.credentials_file = os.path.join(config_dir, credentials_filename)

        # 3) If credentials file does not exist, defer error
        if not os.path.exists(self.credentials_file):
            self._credentials_missing = True
        else:
            self._load_credentials()

    def _load_credentials(self):
        """Load the credentials file."""
        self.credentials = configparser.ConfigParser()
        self.credentials.read(self.credentials_file)
        self._credentials_missing = False


    @staticmethod
    def get_instance(config_file=None):
        if ConfigReader._instance is None:
            ConfigReader._instance = ConfigReader(config_file)
        return ConfigReader._instance

    def _find_config_file(self):
        matches = glob.glob("custom/*/config/config.ini", recursive=True)
        if not matches:
            raise FileNotFoundError("No config.ini file found in custom/*/config/")
        return matches[0]

    def get(self, section: str, key: str, fallback=None):
        return self.config.get(section, key, fallback=fallback)

    def get_default(self, key: str, fallback=None):
        return self.config.get("DEFAULT", key, fallback=fallback)

    def get_connection(self, key: str, fallback=None):
        if self._credentials_missing:
            raise FileNotFoundError("Credentials file not yet set up.")
        return self.credentials.get("CREDENTIALS", key, fallback=fallback)

    def get_config_directory(self):
        """Return the directory containing the config file."""
        return os.path.dirname(self.config_file)

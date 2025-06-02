from pathlib import Path
import os
import datetime
from config_reader import ConfigReader

class PathManager:
    def __init__(self):
        self.config = ConfigReader.get_instance()
        self.base_path = Path(self.config.get("PATHS", "base_path"))

    def get_path(self, section, key, check_path=True, **format_kwargs):
        path = self.config.get(section, key)
        if path is None:
            return None

        # Add timestamp and any format kwargs (like prefix)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path = path.replace("{timestamp}", timestamp)
        for k, v in format_kwargs.items():
            path = path.replace(f"{{{k}}}", v)

        full_path = self.base_path / path
        if check_path:
            os.makedirs(full_path.parent, exist_ok=True)

        return full_path

    def get_template_path(self, template_name):
        template_base_path = "templates"
        template_path = Path(template_base_path) / template_name
        return template_path
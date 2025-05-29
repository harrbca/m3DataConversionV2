from pathlib import Path
import os
import shutil
from config_reader import ConfigReader

class BasePathInitializer:
    def __init__(self):
        # Use ConfigReader to locate the config file and base path
        self.config_reader = ConfigReader.get_instance()
        self.base_path = Path(self.config_reader.get("DEFAULT", "base_path"))

        if not self.base_path:
            raise ValueError("Base path is not defined in the configuration file.")

    def create_base_path(self):
        # Ensure the base path exists
        if not self.base_path.exists():
            try:
                os.makedirs(self.base_path, exist_ok=True)
                print(f"Base path created: {self.base_path}")
            except PermissionError as e:
                raise PermissionError(f"Permission denied to create path: {self.base_path}") from e
            except Exception as e:
                raise Exception(f"Error creating the base path: {e}") from e
        else:
            print(f"Base path already exists: {self.base_path}")

    def copy_example_credentials(self):
        # Define the static location of the example credentials file
        example_file = Path("config/credentials.ini.example")
        credentials_file = self.base_path / "credentials.ini"

        # Copy the credentials example file to the base path if it doesn't already exist
        if not credentials_file.exists():
            if example_file.exists():
                try:
                    shutil.copy(example_file, credentials_file)
                    print(f"Copied credentials file from {example_file} to {credentials_file}")
                except PermissionError as e:
                    raise PermissionError(f"Permission denied to copy file: {example_file}") from e
                except Exception as e:
                    raise Exception(f"Error copying credentials file: {e}") from e
            else:
                raise FileNotFoundError(f"Example credentials file not found at: {example_file}")
        else:
            print(f"Credentials file already exists at: {credentials_file}")


def main():
    try:
        # Initialize the base path
        initializer = BasePathInitializer()
        initializer.create_base_path()
        initializer.copy_example_credentials()

        # Initialize ConfigReader after ensuring base_path and credentials
        print("ConfigReader initialized successfully.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
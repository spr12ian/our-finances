from our_finances.classes.config import Config
from our_finances.classes.os_helper import OsHelper
from pathlib import Path
from typing import Optional


class FileHelper:
    def __init__(self, file_path: Optional[Path] = None):
        self.file_path = file_path

    def overwrite(self):
        if file_path := self.file_path:
            with open(file_path, "w"):
                pass
        else:
            raise ValueError("file_path is not set.")

    def append(self, message: str = ""):
        if file_path := self.file_path:
            with open(file_path, "a") as file:
                file.write(message + "\n")
        else:
            raise ValueError("file_path is not set.")

    def set_output_from_file(self, file_path: Path) -> None:
        self.file_path = self.get_output_path(file_path)
        self.overwrite()

    def get_output_path(
        self, file_path: Path, output_directory: Optional[Path] = None
    ) -> Path:
        """
        Get the output path for a file based on the output directory.
        """
        if output_directory is None:
            config = Config()
            output_directory = Path(config.get("OUTPUT_DIRECTORY"))

        stem = OsHelper().get_stem(file_path)
        return output_directory / f"{stem}.txt"

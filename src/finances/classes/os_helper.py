import os
from pathlib import Path

class OsHelper:
    def file_exists(self, path: Path) -> bool:
        return os.path.isfile(path)

    def get_basename(self, path: Path) -> str:
        return os.path.basename(path)

    def get_extension(self, path: Path) -> str:
        return os.path.splitext(os.path.basename(path))[1]

    def get_home_directory(self) -> str:
        return os.path.expanduser("~")

    def get_stem(self, path: Path) -> str:
        return os.path.splitext(os.path.basename(path))[0]

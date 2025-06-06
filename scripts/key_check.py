# ruff: noqa: E402
from scripts.bootstrap import setup_path

setup_path()

from pathlib import Path

from finances.classes.file_helper import FileHelper
from finances.classes.google_helper import GoogleHelper


def main() -> None:

    goo = GoogleHelper()

    # Define the required scopes
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    ]

    spreadsheet = goo.get_spreadsheet(scopes)

    f = FileHelper()
    f.set_output_from_file(Path(__file__))

    f.append(
        f'Successfully connected to "{spreadsheet.title}" Google Sheets spreadsheet'
    )


if __name__ == "__main__":
    main()

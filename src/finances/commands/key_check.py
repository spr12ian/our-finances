from our_finances.classes.file_helper import FileHelper
from our_finances.classes.google_helper import GoogleHelper
from our_finances.classes.log_helper import debug_function_call
from pathlib import Path
from typing import Any


@debug_function_call
def main(args: Any = None) -> None:
    if len(args) > 0:
        print("This command does not accept any arguments.")
        return

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

import sys

from scripts.bootstrap import setup_path

setup_path()


from finances.classes.google_helper import GoogleHelper, GoogleHelperError


def getSpreadsheetName() -> str:
    try:
        goo = GoogleHelper()

        # Define the required scopes
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets.readonly",
            "https://www.googleapis.com/auth/drive.readonly",
        ]

        spreadsheet = goo.get_spreadsheet(scopes)

    except GoogleHelperError as e:
        print(f"Error initialising GoogleHelper: {e}")

        if e.__cause__:
            print(f"Root cause: {type(e.__cause__).__name__}: {e.__cause__}")

        sys.exit(1)

    return spreadsheet.title


def main() -> None:
    spreadsheet_name = getSpreadsheetName()

    print(f'Successfully connected to "{spreadsheet_name}" Google Sheets spreadsheet')


if __name__ == "__main__":
    main()

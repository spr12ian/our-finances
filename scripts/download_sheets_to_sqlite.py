from scripts.bootstrap import setup_path

setup_path()

from finances.classes.spreadsheet_to_sqlite import SpreadSheetToSqlite


def main() -> None:
    print("Converting Google Sheets spreadsheet to SQLite database\n")

    converter = SpreadSheetToSqlite()

    # Convert spreadsheet to SQLite
    converter.convert_to_sqlite()

    print("Converted Google Sheets spreadsheet to SQLite database")


if __name__ == "__main__":
    main()

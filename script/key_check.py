from script.bootstrap import setup_path

setup_path()


from finances.classes.google_helper import GoogleHelper


def main() -> None:

    goo = GoogleHelper()

    # Define the required scopes
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    ]

    spreadsheet = goo.get_spreadsheet(scopes)

    print(f'Successfully connected to "{spreadsheet.title}" Google Sheets spreadsheet')


if __name__ == "__main__":
    main()

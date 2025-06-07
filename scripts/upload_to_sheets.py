# scripts/upload_to_sheets.py

from finances.classes.google import get_gspread_client
from finances.loader import load_sqlite_data  # Or whatever loader you have


def main():
    gc = get_gspread_client()  # your existing service account logic
    spreadsheet = gc.open_by_key("your-spreadsheet-key")

    # Example: upload transactions
    worksheet = spreadsheet.worksheet("TransactionsX")
    data = load_sqlite_data("transactions")  # a function you write or reuse

    # Clear & update
    worksheet.clear()
    worksheet.update([list(data[0].keys())] + [list(row.values()) for row in data])

if __name__ == "__main__":
    main()

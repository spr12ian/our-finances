# import standard files
import time
from pathlib import Path
from typing import Any

# import pip files
from gspread.worksheet import Worksheet
from our_finances.util.string_helpers import crop

# import local files
from finances.classes.file_helper import FileHelper
from finances.classes.google_helper import GoogleHelper
from finances.classes.pandas_helper import PandasHelper
from finances.classes.sqlalchemy_helper import valid_sqlalchemy_name

TYPE_MAPPING = {
    " (£)": {
        "to_db": "to_numeric_str",
        "sqlite_type": "TEXT",
        "from_db": "from_decimal_2",
        "python_type": "Decimal",
        "sqlalchemy_type": "DECIMAL",
    },
    " (%)": {
        "to_db": "to_numeric_str",
        "sqlite_type": "TEXT",
        "from_db": "from_decimal",
        "python_type": "Decimal",
        "sqlalchemy_type": "DECIMAL",
    },
    "?": {
        "to_db": "to_boolean_integer",
        "sqlite_type": "INTEGER",
        "from_db": "from_boolean_integer",
        "python_type": "bool",
        "sqlalchemy_type": "Integer",
    },
    "Date": {
        "to_db": "to_date",
        "sqlite_type": "TEXT",
        "from_db": "from_str",
        "python_type": "str",
        "sqlalchemy_type": "Date",
    },
}


class SpreadsheetAnalyzer:
    def __init__(self) -> None:
        """
        Initialize the analyzer
        """

        # Define the required scopes
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets.readonly",
            "https://www.googleapis.com/auth/drive.readonly",
        ]

        self.spreadsheet = GoogleHelper().get_spreadsheet(scopes)

        self.pdh = PandasHelper()

        # List of list items which are table_name, column_name
        self.fields: list[list[str]] = []

        self.account_sheet_names: list[str] = []

        self.all_sheet_names: list[str] = []

    def analyze_spreadsheet(self) -> None:
        """
        Analyze all sheets in the Google Spreadsheet
        """

        # Iterate through all worksheets
        for worksheet in self.spreadsheet.worksheets():
            self.analyze_worksheet(worksheet)

            time.sleep(1.1)  # Prevent Google API rate limiting

    def analyze_worksheet(self, worksheet: Worksheet) -> None:

        self.all_sheet_names.append(worksheet.title)
        if worksheet.title.startswith("_"):
            self.account_sheet_names.append(worksheet.title)

        table_name = valid_sqlalchemy_name(worksheet.title)

        pdh = self.pdh
        first_row = worksheet.row_values(1)

        # Split columns and rows
        df = pdh.header_to_dataframe(first_row)
        for col in df.columns:
            self.fields.append(self.get_column_types(table_name, col))

    def get_column_types(
        self, table_name: str, spreadsheet_column_name: str
    ) -> list[str]:

        # sqlite_type is used to write the spreadsheet column value to the database
        # The sqlite_type may cause the spreadsheet string to be transformed

        # python_type is used when reading the database column value from the database
        # i.e. read the sqlite value and format as python type

        sqlite_column_name = valid_sqlalchemy_name(spreadsheet_column_name)
        for type_map_key, type_info in TYPE_MAPPING.items():
            if spreadsheet_column_name.endswith(type_map_key):
                if type_map_key == "?":  # Only for boolean columns
                    sqlite_column_name = sqlite_column_name.strip("_")
                elif type_map_key != "?":  # For the other special cases
                    sqlite_column_name = crop(sqlite_column_name, "____")

                return [
                    table_name,
                    spreadsheet_column_name,
                    sqlite_column_name,
                    type_info["to_db"],
                    type_info["sqlite_type"],
                    type_info["from_db"],
                    type_info["python_type"],
                    type_info["sqlalchemy_type"],
                ]

            if spreadsheet_column_name.startswith(type_map_key):
                return [
                    table_name,
                    spreadsheet_column_name,
                    sqlite_column_name,
                    type_info["to_db"],
                    type_info["sqlite_type"],
                    type_info["from_db"],
                    type_info["python_type"],
                    type_info["sqlalchemy_type"],
                ]

        sqlite_type = "TEXT"
        python_type = "str"
        to_db = "to_str"
        from_db = "from_str"
        sqlalchemy_type = "String"

        return [
            table_name,
            spreadsheet_column_name,
            sqlite_column_name,
            to_db,
            sqlite_type,
            from_db,
            python_type,
            sqlalchemy_type,
        ]

    def write_get_account_sheet_names_js(self) -> None:
        lines = ["function getAccountSheetNames() {"]
        lines.append("  return" + str(self.account_sheet_names))
        lines.append("}")
        output_str = "\n".join(lines)
        Path("get_account_sheet_names.js").write_text(output_str)

    def write_account_sheet_names_py(self) -> None:
        lines = ["ACCOUNT_SHEET_NAMES=" + str(self.account_sheet_names)]
        output_str = "\n".join(lines)
        Path("account_sheet_names.py").write_text(output_str)

    def write_get_all_sheet_names_js(self) -> None:
        lines = ["function getAllSheetNames() {"]
        lines.append("  return" + str(self.all_sheet_names))
        lines.append("}")
        output_str = "\n".join(lines)
        Path("get_all_sheet_names.js").write_text(output_str)

    def write_spreadsheet_fields_py(self) -> None:
        prefix = self.get_prefix()
        fields_output = self.get_fields_output()
        output_str = prefix + fields_output
        Path("spreadsheet_fields.py").write_text(output_str)

    def get_fields_output(self) -> str:
        return str(self.fields)

    def get_prefix(self) -> str:
        prefix = """# spreadsheet_fields.py
def get_field_by_spreadsheet_column_name(table_name:str, spreadsheet_column_name:str):
    for field in fields:
        if field[1] == spreadsheet_column_name and field[0] == table_name:
            return field
    return None

def get_field_by_sqlite_column_name(table_name:str, sqlite_column_name:str):
    for field in fields:
        if field[2] == sqlite_column_name and field[0] == table_name:
            return field
    return None

def get_from_db(table_name:str, column_name:str):
    field = get_field_by_sqlite_column_name(
        table_name, column_name
    )
    return field[5] # from_db

def get_python_type(table_name:str, column_name:str):
    field = get_field_by_sqlite_column_name(
        table_name, column_name
    )
    return field[6] # python_type

def get_sqlalchemy_type(table_name:str, column_name:str):
    field = get_field_by_sqlite_column_name(
        table_name, column_name
    )
    return field[7] # sqlalchemy_type

def get_sqlite_type(table_name:str, column_name:str):
    field = get_field_by_sqlite_column_name(
        table_name, column_name
    )
    return field[4] # sqlite_type

def get_to_db(table_name:str, column_name:str):
    field = get_field_by_sqlite_column_name(
        table_name, column_name
    )
    return field[3] # to_db

# table_name, spreadsheet_column_name, sqlite_column_name, to_db, sqlite_type, from_db, python_type, sqlalchemy_type
fields = """
        return prefix


def main(args: Any = None) -> None:
    if len(args) > 0:
        print("This command does not accept any arguments.")
        return

    analyzer = SpreadsheetAnalyzer()

    # Analyze spreadsheet
    analyzer.analyze_spreadsheet()

    analyzer.write_account_sheet_names_py()
    analyzer.write_get_account_sheet_names_js()
    analyzer.write_get_all_sheet_names_js()
    analyzer.write_spreadsheet_fields_py()

    f = FileHelper()
    f.set_output_from_file(Path(__file__))
    f.append("Analyzed Google Sheets spreadsheet")

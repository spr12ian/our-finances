from scripts.bootstrap import setup_path

setup_path()

# import standard files
import time
from pathlib import Path

# import pip files
from gspread.worksheet import Worksheet

# import local files
from finances.classes.google_helper import GoogleHelper
from finances.classes.pandas_helper import PandasHelper
from finances.classes.spreadsheet_field import SpreadsheetField
from finances.classes.sqlalchemy_helper import valid_sqlalchemy_name
from finances.util.string_helpers import crop

GENERATED_DIR = "src/finances/generated/"

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

        self.fields: list[SpreadsheetField] = []

        self.account_sheet_names: list[str] = []

        self.all_sheet_names: list[str] = []

    def analyze_spreadsheet(self) -> None:
        """
        Analyze all sheets in the Google Spreadsheet
        """

        # Iterate through all worksheets
        for worksheet in self.spreadsheet.worksheets():
            print(f"Analyzing {worksheet.title}")
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
    ) -> SpreadsheetField:
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

                return SpreadsheetField(
                    table_name,
                    spreadsheet_column_name,
                    sqlite_column_name,
                    type_info["to_db"],
                    type_info["sqlite_type"],
                    type_info["from_db"],
                    type_info["python_type"],
                    type_info["sqlalchemy_type"],
                )

            if spreadsheet_column_name.startswith(type_map_key):
                return SpreadsheetField(
                    table_name,
                    spreadsheet_column_name,
                    sqlite_column_name,
                    type_info["to_db"],
                    type_info["sqlite_type"],
                    type_info["from_db"],
                    type_info["python_type"],
                    type_info["sqlalchemy_type"],
                )

        sqlite_type = "TEXT"
        python_type = "str"
        to_db = "to_str"
        from_db = "from_str"
        sqlalchemy_type = "String"

        return SpreadsheetField(
            table_name,
            spreadsheet_column_name,
            sqlite_column_name,
            to_db,
            sqlite_type,
            from_db,
            python_type,
            sqlalchemy_type,
        )

    def get_pre_pre_prefix(self) -> str:
        return (
            '"""Automatically generated file.\n\n'
            "To update, run python3 -m script.analyze_spreadsheet\n\n"
            '"""\n'
        )

    def write_account_sheet_names_py(self) -> None:
        lines = ["ACCOUNT_SHEET_NAMES = ["]
        for sheet_name in self.account_sheet_names:
            lines.append(f'    "{sheet_name}",')
        lines.append("]")
        self.write_lines("account_sheet_names.py", lines)

    def write_field_registry_py(self) -> None:
        pre_pre_prefix = self.get_pre_pre_prefix()
        lines = [pre_pre_prefix]
        prefix = Path("data/raw/field_registry_prefix.py").read_text()
        lines.append(prefix)
        lines.append("SPREADSHEET_FIELDS: Final[list[SF]] = [")
        for field in self.fields:
            lines.append(f"    {field.short()},")
        lines.append("]")
        lines.append("")
        lines.append("field_registry = FieldRegistry(SPREADSHEET_FIELDS)")
        self.write_lines("field_registry.py", lines)

    def write_files(self) -> None:
        self.write_account_sheet_names_py()
        self.write_get_account_sheet_names_js()
        self.write_get_all_sheet_names_js()
        self.write_field_registry_py()

    def write_get_account_sheet_names_js(self) -> None:
        lines = ["function getAccountSheetNames() {"]
        lines.append("  return" + str(self.account_sheet_names))
        lines.append("}")
        self.write_lines("get_account_sheet_names.js", lines)

    def write_get_all_sheet_names_js(self) -> None:
        lines = ["function getAllSheetNames() {"]
        lines.append("  return" + str(self.all_sheet_names))
        lines.append("}")
        self.write_lines("get_all_sheet_names.js", lines)

    def write_lines(self, file_name: str, lines: list[str]) -> None:
        output_str = "\n".join(lines)
        output_file = f"{GENERATED_DIR}{file_name}"
        Path(output_file).write_text(output_str)
        print(f"Code at {output_file} should be checked")

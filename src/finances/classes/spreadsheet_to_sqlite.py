import time
from collections.abc import Callable
from typing import Any, Final

from gspread import Worksheet
from pandas import DataFrame, Series

from finances.classes.config import Config
from finances.classes.google_helper import GoogleHelper
from finances.classes.pandas_helper import PandasHelper
from finances.classes.sqlite_helper import SQLiteHelper, to_sqlite_name
from finances.generated.field_registry import field_registry
from finances.util.boolean_helpers import boolean_string_to_int
from finances.util.database_keys import get_primary_key_columns, has_primary_key
from finances.util.date_helpers import UK_to_ISO
from finances.util.financial_helpers import string_to_financial
from finances.util.string_helpers import crop, remove_non_numeric


class SpreadSheetToSqliteError(Exception):
    pass


class SpreadSheetToSqlite:
    _SCALARS: Final[dict[str, Callable[[str], Any] | None]] = {
        "to_boolean_integer": boolean_string_to_int,
        "to_date": UK_to_ISO,
        "to_financial": string_to_financial,
        "to_numeric_str": remove_non_numeric,
        "to_str": None,
    }

    def __init__(self) -> None:
        """
        Initialize the converter with Google Sheets credentials and spreadsheet name

        Args:
            credentials_path (str): Path to your Google Cloud service account JSON
            spreadsheet_name (str): Name of the Google Spreadsheet
        """

        self.read_config()

        self.pdh = PandasHelper()

        # Define the required scopes
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets.readonly",
            "https://www.googleapis.com/auth/drive.readonly",
        ]

        self.spreadsheet = GoogleHelper().get_spreadsheet(scopes)

        self.sql = SQLiteHelper()

    @staticmethod
    def apply(df: DataFrame, column_name: str, scalar: Callable[[Any], Any]) -> Series:  # type: ignore
        return df[column_name].apply(scalar)  # type: ignore

    def backup_bmonzo(self) -> None:
        pass

    def convert_column_name(self, spreadsheet_column_name: str) -> str:
        sqlite_column_name = to_sqlite_name(spreadsheet_column_name)

        if spreadsheet_column_name.endswith(" (£)"):
            sqlite_column_name = crop(sqlite_column_name, "____")
        elif spreadsheet_column_name.endswith(" (%)"):
            sqlite_column_name = crop(sqlite_column_name, "____")
        elif spreadsheet_column_name.endswith("?"):
            sqlite_column_name = sqlite_column_name.strip("_")

        return sqlite_column_name

    def convert_df_col(
        self, df: DataFrame, table_name: str, column_name: str
    ) -> DataFrame:
        to_db = self.get_to_db(table_name, column_name)
        if to_db not in self._SCALARS:
            raise ValueError(f"Unexpected to_db value: {to_db}")

        scalar = self._SCALARS[to_db]
        if scalar:
            print(f"Transforming {table_name}.{column_name} using {to_db}")

            df[column_name] = self.apply(df, column_name, scalar)  # type: ignore

        return df

    def convert_to_sqlite(self) -> None:
        """
        Convert all sheets in the Google Spreadsheet to SQLite tables
        """
        self.sql.open_connection()

        self.backup_bmonzo()

        # Iterate through all worksheets
        for worksheet in self.spreadsheet.worksheets():
            if self.convert_account_tables or not worksheet.title.startswith("_"):
                self.convert_worksheet(worksheet)

                time.sleep(1.1)  # Prevent Google API rate limiting

        self.backup_bmonzo()

        self.sql.close_connection()

    def convert_worksheet(self, worksheet: Worksheet) -> None:
        table_name = to_sqlite_name(worksheet.title)
        print(f"table_name: {table_name}")

        pdh = self.pdh

        # Get worksheet data as a DataFrame
        data = worksheet.get_all_values()

        # Split columns and rows
        df = pdh.worksheet_values_to_dataframe(data)

        df.columns = [self.convert_column_name(col) for col in df.columns]

        for col in df.columns:
            print(
                f"Original header: {repr(col)} → Converted: {self.convert_column_name(col)}"
            )

        # Validate column headers
        original_headers = df.columns.tolist()
        if any(col.strip() == "" for col in original_headers):
            raise SpreadSheetToSqliteError(
                f"Empty column name(s) in worksheet '{table_name}': {original_headers}"
            ) from ValueError

        for col in df.columns:
            df = self.convert_df_col(df, table_name, col)

        if has_primary_key(table_name):
            primary_key_columns = get_primary_key_columns(table_name)
            key_column = primary_key_columns[0]
            if key_column not in df.columns:
                raise ValueError(self.key_column_not_found(worksheet.title, key_column))
            sqlite_type = self.get_sqlite_type(table_name, key_column)
            dtype = {key_column: f"{sqlite_type} PRIMARY KEY"}
        else:
            # Add 'id' column and populate with values
            df.insert(0, "id", range(1, len(df) + 1))  # type: ignore
            dtype = {"id": "INTEGER PRIMARY KEY AUTOINCREMENT"}

        print(f"table_name: {table_name}")
        print(f"dtype: {dtype}")

        # Write DataFrame to SQLite table (sheet name becomes table name)
        df.to_sql(
            table_name,
            self.sql.db_connection,
            if_exists="replace",
            index=False,
            dtype=dtype,
        )

    def get_financial_columns(self) -> list[str]:
        return [
            "balance",
            "credit",
            "debit",
        ]

    def get_sqlite_type(self, table_name: str, column_name: str) -> str:
        return field_registry.get_sqlite_type(table_name, column_name)

    def get_to_db(self, table_name: str, column_name: str) -> str:
        return field_registry.get_to_db(table_name, column_name)

    def key_column_not_found(self, sheet_name: str, key_column: str) -> str:
        return (
            f"Primary key column '{key_column}' not found in worksheet '{sheet_name}'"
        )

    def read_config(self) -> None:
        config = Config()

        self.convert_account_tables = config.get("CONVERT_ACCOUNT_TABLES", True)

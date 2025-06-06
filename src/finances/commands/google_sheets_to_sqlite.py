import time
from pandas import DataFrame
from typing import Any

from gspread import Worksheet
from our_finances.classes.config import Config
from our_finances.classes.google_helper import GoogleHelper
from our_finances.classes.pandas_helper import PandasHelper
from our_finances.classes.sql_helper import SQL_Helper
from our_finances.classes.sqlalchemy_helper import valid_sqlalchemy_name
from our_finances.util.string_helpers import crop
from database_keys import get_primary_key_columns, has_primary_key
import spreadsheet_fields


class SpreadsheetToSqliteDb:
    def __init__(self):
        """
        Initialize the converter with Google Sheets credentials and spreadsheet name

        Args:
            credentials_path (str): Path to your Google Cloud service account JSON
            spreadsheet_name (str): Name of the Google Spreadsheet
        """

        config = Config()

        self.convert_account_tables = config.get("CONVERT_ACCOUNT_TABLES")

        self.pdh = PandasHelper()

        # Define the required scopes
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets.readonly",
            "https://www.googleapis.com/auth/drive.readonly",
        ]

        self.spreadsheet = GoogleHelper().get_spreadsheet(scopes)

        self.sql = SQL_Helper().select_sql_helper("SQLite")

    def convert_column_name(self, spreadsheet_column_name: str) -> str:
        sqlite_column_name = valid_sqlalchemy_name(spreadsheet_column_name)

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
        sqlite_type = self.get_sqlite_type(table_name, column_name)
        to_db = self.get_to_db(table_name, column_name)
        match to_db:
            case "to_boolean_integer":
                df[column_name] = df[column_name].apply(uf.boolean_string_to_int)
            case "to_date":
                df[column_name] = df[column_name].apply(uf.UK_to_ISO)
            case "to_numeric_str":
                df[column_name] = df[column_name].apply(uf.remove_non_numeric)
            case "to_str":
                pass
            case _:
                raise ValueError(f"Unexpected to_db value: {to_db}")

        return df

    def convert_to_sqlite(self):
        """
        Convert all sheets in the Google Spreadsheet to SQLite tables
        """
        self.sql.open_connection()

        # Iterate through all worksheets
        for worksheet in self.spreadsheet.worksheets():
            if self.convert_underscore_tables or not worksheet.title.startswith("_"):
                self.convert_worksheet(worksheet)

                time.sleep(1.1)  # Prevent Google API rate limiting

        self.sql.close_connection()

    def convert_worksheet(self, worksheet:Worksheet):
        table_name = valid_sqlalchemy_name(worksheet.title)

        pdh = self.pdh

        # Get worksheet data as a DataFrame
        data = worksheet.get_all_values()

        try:
            # Split columns and rows
            df = pdh.worksheet_values_to_dataframe(data)

            df.columns = [self.convert_column_name(col) for col in df.columns]

            for col in df.columns:
                df = self.convert_df_col(df, table_name, col)

            if has_primary_key(table_name):
                primary_key_columns = get_primary_key_columns(table_name)
                key_column = primary_key_columns[0]
                if key_column not in df.columns:
                    raise ValueError(
                        f"Primary key column '{key_column}' not found in worksheet '{worksheet.title}'"
                    )
                sqlite_type = self.get_sqlite_type(table_name, key_column)
                dtype = {key_column: f"{sqlite_type} PRIMARY KEY"}
            else:
                # Add 'id' column and populate with values
                df.insert(0, "id", range(1, len(df) + 1))
                dtype = {"id": "INTEGER PRIMARY KEY AUTOINCREMENT"}

        except Exception as e:
            self.l.error(f"Error converting worksheet {worksheet.title}: {e}")
            raise

        # Write DataFrame to SQLite table (sheet name becomes table name)
        df.to_sql(
            table_name,
            self.sql.db_connection,
            if_exists="replace",
            index=False,
            dtype=dtype,
        )
        # self.l.debug(f'Written {table_name}')

    def get_sqlite_type(self, table_name, column_name):
        return spreadsheet_fields.get_sqlite_type(table_name, column_name)

    def get_to_db(self, table_name, column_name):
        return spreadsheet_fields.get_to_db(table_name, column_name)


def main(args: Any = None) -> None:
    if len(args) > 0:
        print("This command does not accept any arguments.")
        return
    
    print(f"Converting Google Sheets spreadsheet to SQLite database\n")

    converter = SpreadsheetToSqliteDb()

    # Convert spreadsheet to SQLite
    converter.convert_to_sqlite()

    print(f"Converted Google Sheets spreadsheet to SQLite database")


if __name__ == "__main__":
    main()

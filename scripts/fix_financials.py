from script.bootstrap import setup_path

setup_path()


from gspread.worksheet import Worksheet
from pandas import DataFrame

from finances.classes.google_helper import GoogleHelper
from finances.classes.pandas_helper import PandasHelper
from finances.classes.sql_helper import SQL_Helper
from finances.classes.sqlalchemy_helper import valid_sqlalchemy_name
from finances.util.financial_helpers import string_to_financial


def convert(df: DataFrame, financial_column: str) -> DataFrame:
    df[financial_column] = df[financial_column].apply(string_to_financial)  # type: ignore
    return df


class SpreadsheetToSqliteDb:
    def __init__(self) -> None:
        """
        Initialize the converter with Google Sheets credentials and spreadsheet name

        Args:
            credentials_path (str): Path to your Google Cloud service account JSON
            spreadsheet_name (str): Name of the Google Spreadsheet
        """

        self.pdh = PandasHelper()

        # Define the required scopes
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets.readonly",
            "https://www.googleapis.com/auth/drive.readonly",
        ]

        self.spreadsheet = GoogleHelper().get_spreadsheet(scopes)

        self.sql = SQL_Helper().select_sql_helper("SQLite")

    def convert_to_sqlite(self) -> None:
        """
        Convert sheet in the Google Spreadsheet to SQLite table
        """
        self.sql.open_connection()

        worksheet = self.spreadsheet.worksheets()[0]

        self.convert_worksheet(worksheet)

        self.sql.close_connection()

    def convert_worksheet(self, worksheet: Worksheet) -> None:

        table_name = valid_sqlalchemy_name(worksheet.title)

        pdh = self.pdh

        # Get worksheet data as a DataFrame
        data = worksheet.get_all_values()

        # Split columns and rows
        df = pdh.worksheet_values_to_dataframe(data)
        df.columns = [valid_sqlalchemy_name(col) for col in df.columns]

        for financial_column in get_financial_columns():
            if financial_column in df.columns:
                try:
                    df = convert(df, financial_column)
                except:
                    print(financial_column)
                    raise

        # Write DataFrame to SQLite table (sheet name becomes table name)
        df.to_sql(
            table_name,
            self.sql.db_connection,
            if_exists="replace",
            index=False,
        )


def main() -> None:
    converter = SpreadsheetToSqliteDb()
    converter.convert_to_sqlite()


if __name__ == "__main__":
    main()

from our_finances.classes.google_helper import GoogleHelper
from pandas_helper import PandasHelper
from sql_helper import SQL_Helper
from sqlalchemy_helper import valid_sqlalchemy_name
from our_finances.classes.log_helper import LogHelper
from decimal import Decimal, InvalidOperation
import re

l = LogHelper(__file__)
l.set_level_debug()
l.debug(__file__)


# Function to convert currency/percent strings to float
def string_to_financial(string: str) -> Decimal:
    if string.strip() == "":  # Check if the string is empty or whitespace
        return Decimal("0.00")

    # Remove any currency symbols and thousand separators
    string = re.sub(r"[^\d.,%]", "", string)
    string = string.replace(",", "")

    # Check if the string has a percentage symbol
    if "%" in string:
        string = string.replace("%", "")
        try:
            return Decimal(string) / Decimal("100")
        except InvalidOperation:
            return Decimal("0.00")

    try:
        return Decimal(string)
    except InvalidOperation:
        return Decimal("0.00")


def convert(df):
    l.debug("convert")
    for financial_column in get_financial_columns():
        if financial_column in df.columns:
            try:
                df[financial_column] = df[financial_column].apply(string_to_financial)
                l.debug(f"df[financial_column].dtype: {df[financial_column].dtype}")
                l.debug(f"df[financial_column].head: {df[financial_column].head}")
                l.debug(
                    f"df[financial_column].describe: {df[financial_column].describe}"
                )
            except:
                print(financial_column)
                raise
    return df


def get_financial_columns():
    return [
        "balance",
        "credit",
        "debit",
    ]


class SpreadsheetToSqliteDb:
    def __init__(self):
        """
        Initialize the converter with Google Sheets credentials and spreadsheet name

        Args:
            credentials_path (str): Path to your Google Cloud service account JSON
            spreadsheet_name (str): Name of the Google Spreadsheet
        """
        self.l = LogHelper("SpreadsheetToSqliteDb")
        self.l.set_level_debug()

        self.log = LogHelper("SpreadsheetToSqliteDb")
        self.pdh = PandasHelper()

        # Define the required scopes
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets.readonly",
            "https://www.googleapis.com/auth/drive.readonly",
        ]

        self.spreadsheet = GoogleHelper().get_spreadsheet(scopes)

        self.sql = SQL_Helper().select_sql_helper("SQLite")

    def convert_to_sqlite(self):
        """
        Convert sheet in the Google Spreadsheet to SQLite table
        """
        self.sql.open_connection()

        worksheet = self.spreadsheet.worksheets()[0]

        self.convert_worksheet(worksheet)

        self.sql.close_connection()

    def convert_worksheet(self, worksheet):
        self.log.info(f"Converting {worksheet.title}")

        table_name = valid_sqlalchemy_name(worksheet.title)
        self.log.info(f"table_name: {table_name}")

        pdh = self.pdh

        # Get worksheet data as a DataFrame
        data = worksheet.get_all_values()

        try:
            self.l.debug("In the try block")
            # Split columns and rows
            df = pdh.worksheet_values_to_dataframe(data)
            df.columns = [valid_sqlalchemy_name(col) for col in df.columns]
            df = convert(df)

        except Exception as e:
            self.l.error(f"Error converting worksheet {worksheet.title}: {e}")
            raise

        self.l.debug(f"Writing {table_name}")
        self.l.debug(f"df: {df}")
        # Write DataFrame to SQLite table (sheet name becomes table name)
        df.to_sql(
            table_name,
            self.sql.db_connection,
            if_exists="replace",
            index=False,
        )
        self.l.debug(f"Written {table_name}")


def main():
    converter = SpreadsheetToSqliteDb()
    converter.convert_to_sqlite()


if __name__ == "__main__":
    main()

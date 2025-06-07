from finances.classes.spreadsheet_field import SpreadsheetField


class FieldRegistry:
    def __init__(self, field_list: list[SpreadsheetField]) -> None:
        self._fields: list[SpreadsheetField] = field_list
        self._by_spreadsheet: dict[tuple[str, str], SpreadsheetField] = {}
        self._by_sqlite: dict[tuple[str, str], SpreadsheetField] = {}

        for field in field_list:
            self._by_spreadsheet[(field.table_name, field.spreadsheet_column_name)] = (
                field
            )
            self._by_sqlite[(field.table_name, field.sqlite_column_name)] = field

    def get_by_spreadsheet(self, table: str, spreadsheet_col: str) -> SpreadsheetField:
        try:
            return self._by_spreadsheet[(table, spreadsheet_col)]
        except KeyError:
            raise KeyError(
                f"Field not found for table '{table}', spreadsheet column '{spreadsheet_col}'"
            )

    def get_by_sqlite(self, table: str, sqlite_col: str) -> SpreadsheetField:
        try:
            return self._by_sqlite[(table, sqlite_col)]
        except KeyError:
            raise KeyError(
                f"Field not found for table '{table}', sqlite column '{sqlite_col}'"
            )

    def get_sqlite_type(self, table: str, col: str) -> str:
        return self.get_by_sqlite(table, col).sqlite_type

    def get_python_type(self, table: str, col: str) -> str:
        return self.get_by_sqlite(table, col).python_type

    def get_sqlalchemy_type(self, table: str, col: str) -> str:
        return self.get_by_sqlite(table, col).sqlalchemy_type

    def get_from_db(self, table: str, col: str) -> str:
        return self.get_by_sqlite(table, col).from_db

    def get_to_db(self, table: str, col: str) -> str:
        return self.get_by_sqlite(table, col).to_db

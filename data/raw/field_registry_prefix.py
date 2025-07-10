from __future__ import annotations

from collections.abc import Callable
from typing import Final  # noqa: F401

from finances.classes.spreadsheet_field import SpreadsheetField as SF


class FieldRegistry:
    def __init__(self, field_list: list[SF]) -> None:
        self._fields: list[SF] = field_list
        self._by_spreadsheet: dict[tuple[str, str], SF] = {}
        self._by_sqlite: dict[tuple[str, str], SF] = {}

        for field in field_list:
            self._by_spreadsheet[(field.table_name, field.spreadsheet_column_name)] = (
                field
            )
            self._by_sqlite[(field.table_name, field.sqlite_column_name)] = field

    def __repr__(self) -> str:
        return f"<FieldRegistry {len(self._fields)} fields>"

    def __contains__(self, key: tuple[str, str]) -> bool:
        return key in self._by_spreadsheet or key in self._by_sqlite

    def get_by_spreadsheet(self, table: str, spreadsheet_col: str) -> SF:
        try:
            return self._by_spreadsheet[(table, spreadsheet_col)]
        except KeyError:
            raise KeyError(self.missing(table, spreadsheet_col))

    def missing(self, table: str, spreadsheet_col: str) -> str:
        return (
            f"Field not found for table '{table}', "
            f"spreadsheet column '{spreadsheet_col}'"
        )

    def get_by_sqlite(self, table: str, sqlite_col: str) -> SF:
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


get_field_class: Callable[[], type[SF]] = lambda: SF  # noqa: E731

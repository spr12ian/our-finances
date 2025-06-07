from typing import NamedTuple


class SpreadsheetField(NamedTuple):
    table_name: str
    spreadsheet_column_name: str
    sqlite_column_name: str
    to_db: str
    sqlite_type: str
    from_db: str
    python_type: str
    sqlalchemy_type: str

    def __repr__(self) -> str:
        return (
            f"SpreadsheetField("
            f"{self.table_name!r}, {self.spreadsheet_column_name!r}, "
            f"{self.sqlite_column_name!r}, {self.to_db!r}, "
            f"{self.sqlite_type!r}, {self.from_db!r}, "
            f"{self.python_type!r}, {self.sqlalchemy_type!r})"
        )
    
f=SpreadsheetField('a','b','c','d','e','f','g','h')
print(f"{f!r}")


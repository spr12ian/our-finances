# spreadsheet_fields.py
def get_field_by_spreadsheet_column_name(
    table_name: str, spreadsheet_column_name: str
) -> list[str]:
    for field in fields:
        if field[1] == spreadsheet_column_name and field[0] == table_name:
            return field
    raise KeyError(f"field not found for {table_name}, {spreadsheet_column_name}")


def get_field_by_sqlite_column_name(
    table_name: str, sqlite_column_name: str
) -> list[str]:
    for field in fields:
        if field[2] == sqlite_column_name and field[0] == table_name:
            return field
    raise KeyError(f"field not found for {table_name}, {sqlite_column_name}")


def get_from_db(table_name: str, column_name: str) -> str:
    field = get_field_by_sqlite_column_name(table_name, column_name)
    return field[5]  # from_db


def get_python_type(table_name: str, column_name: str) -> str:
    field = get_field_by_sqlite_column_name(table_name, column_name)
    return field[6]  # python_type


def get_sqlalchemy_type(table_name: str, column_name: str) -> str:
    field = get_field_by_sqlite_column_name(table_name, column_name)
    return field[7]  # sqlalchemy_type


def get_sqlite_type(table_name: str, column_name: str) -> str:
    field = get_field_by_sqlite_column_name(table_name, column_name)
    return field[4]  # sqlite_type


def get_to_db(table_name: str, column_name: str) -> str:
    field = get_field_by_sqlite_column_name(table_name, column_name)
    return field[3]  # to_db


# table_name, spreadsheet_column_name, sqlite_column_name, to_db, sqlite_type, from_db,
# python_type, sqlalchemy_type
fields = [
    ["account_balances", "Key", "key", "to_str", "TEXT", "from_str", "str", "String"],
]

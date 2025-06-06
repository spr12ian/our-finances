from typing import List, Tuple

# table_name, column_name, is_primary_key
database_keys: List[Tuple[str, str, bool]] = [
    ("account_balances", "key", True),
    ("bank_accounts", "key", True),
]


def get_primary_key_columns(table_name: str) -> List[str]:
    """
    Get column_name(s) where the first item equals the given table_name,
    and is_primary_key is True.

    Args:
        table_name (str): The table name to check.

    Returns:
        columns: The primary key column(s).
    """
    columns:list[str] = []
    for table, column, is_primary_key in database_keys:
        if table == table_name and is_primary_key:
            columns.append(column)
    return columns


def has_primary_key(table_name: str) -> bool:
    """
    Check if any tuple exists where the first item equals the given table_name,
    and the third item 'is_primary_key' is True.

    Args:
        table_name (str): The table name to check.

    Returns:
        bool: True if such a tuple exists, False otherwise.
    """
    for table, _, is_primary_key in database_keys:
        if table == table_name and is_primary_key:
            return True
    return False


# # Example usage
# table_name_to_check = "account_balances"
# result = has_primary_key(table_name_to_check)
# print(f"Does the table '{table_name_to_check}' have a primary key defined? {result}")

# primary_key_columns = get_primary_key_columns(table_name_to_check)
# print(f"Primary key column(s) for the table '{table_name_to_check}': {primary_key_columns}")

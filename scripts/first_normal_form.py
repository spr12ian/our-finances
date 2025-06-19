import re
import sqlite3
from typing import Any

from finances.classes.log_helper import LogHelper

l = LogHelper(__file__)
l.set_level_debug()
l.debug(__file__)


def analyze_1nf(db_path: str) -> dict[str, list[dict[str, Any]]]:
    """
    Analyzes an SQLite database for potential First Normal Form violations.

    Returns a dictionary with analysis results for each type of violation.
    """
    violations: dict[str, list[dict[str, Any]]] = {
        "composite_values": [],
        "array_patterns": [],
        "repeating_columns": [],
        "mixed_data_types": [],
    }

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        for table in tables:
            table_name = table[0]

            # Get column information
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()

            # Check for repeating column patterns
            column_names = [col[1] for col in columns]
            check_repeating_columns(table_name, column_names, violations)

            # Sample some data to check for composite values and data type mixing
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 100;")
            rows = cursor.fetchall()

            if rows:
                for col_idx, col in enumerate(columns):
                    col_name = col[1]
                    check_composite_values(
                        table_name, col_name, [row[col_idx] for row in rows], violations
                    )
                    check_data_type_consistency(
                        table_name, col_name, [row[col_idx] for row in rows], violations
                    )

        conn.close()
        return violations

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return violations


def check_repeating_columns(
    table_name: str, column_names: list[str], violations: dict
) -> None:
    """
    Identifies potential repeating column patterns like field1, field2, etc.
    """

    patterns = [
        r"^(.+)[\d]+$",  # Matches field1, field2, etc.
        r"^(.+)_[\d]+$",  # Matches field_1, field_2, etc.
    ]

    for pattern in patterns:
        seen_prefixes = set()
        for col_name in column_names:
            match = re.match(pattern, col_name)
            if match:
                prefix = match.group(1)
                if prefix in seen_prefixes:
                    violations["repeating_columns"].append(
                        {"table": table_name, "pattern": prefix, "example": col_name}
                    )
                    break
                seen_prefixes.add(prefix)


def check_composite_values(
    table_name: str, column_name: str, values: list[Any], violations: dict
) -> None:
    """
    Checks for potential composite values (comma-separated lists, JSON-like strings, etc.)
    """
    l.debug("check_composite_values")
    l.debug(f"table-Name: {table_name}")
    l.debug(f"column_name: {column_name}")
    ignore_composites_with = ["description", "note", "query"]

    for starts_with in ignore_composites_with:
        l.debug(f"starts_with: {starts_with}")
        if column_name.lower().startswith(starts_with):
            return

    patterns = [
        r".*,.*",  # Comma-separated values
        r"^\[.*\]$",  # Array-like values
        r"^\{.*\}$",  # JSON-like values
        r";",  # Semicolon-separated values
        r"\|",  # Pipe-separated values
    ]

    for value in values:
        if value is not None and isinstance(value, str):
            for pattern in patterns:
                if re.search(pattern, value):
                    violations["composite_values"].append(
                        {"table": table_name, "column": column_name, "example": value}
                    )
                    return


def check_data_type_consistency(
    table_name: str, column_name: str, values: list[Any], violations: dict
) -> None:
    """
    Checks for mixed data types within a column
    """
    types_found = set()

    for value in values:
        if value is not None:
            value_type = type(value).__name__
            types_found.add(value_type)

            if len(types_found) > 1:
                violations["mixed_data_types"].append(
                    {
                        "table": table_name,
                        "column": column_name,
                        "types_found": list(types_found),
                    }
                )
                return


def print_analysis_results(violations: dict[str, list[dict[str, Any]]]) -> None:
    """
    Prints the analysis results in a readable format
    """
    print("First Normal Form Violation Analysis\n")

    if not any(violations.values()):
        print("No potential 1NF violations found.")
        return

    if violations["composite_values"]:
        print("\nPotential Composite Values Found:")
        for v in violations["composite_values"]:
            print(f"- Table: {v['table']}, Column: {v['column']}")
            print(f"  Example: {v['example']}")

    if violations["repeating_columns"]:
        print("\nPotential Repeating Column Patterns:")
        for v in violations["repeating_columns"]:
            print(f"- Table: {v['table']}, Pattern: {v['pattern']}*")
            print(f"  Example: {v['example']}")

    if violations["mixed_data_types"]:
        print("\nMixed Data Types in Columns:")
        for v in violations["mixed_data_types"]:
            print(f"- Table: {v['table']}, Column: {v['column']}")
            print(f"  Types found: {', '.join(v['types_found'])}")


def main() -> None:
    db_path = "our_finances.sqlite"
    violations = analyze_1nf(db_path)
    print_analysis_results(violations)


if __name__ == "__main__":
    main()

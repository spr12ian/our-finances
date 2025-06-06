#standard library imports
from decimal import Decimal
from typing import Any, Optional
#pip install imports
import sqlite3
#local imports
from our_finances.classes.config import Config



class SQLiteHelper:
    def __init__(self):
        config = Config()

        self.db_path = config.get("SQLite.database_name")

    def close_connection(self):
        if self.db_connection:
            self.db_connection.close()

    def drop_column(self, table_name: str, column_to_drop: str):
        temp_table_name = f"temp_{table_name}"
        self.open_connection()

        cursor = self.db_connection.cursor()

        # Get the table structure
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

        # Extract column names excluding the column to drop
        column_names = [f'"{col[1]}"' for col in columns if col[1] != column_to_drop]
        column_names_str = ", ".join(column_names)

        # Create a temporary table without the column to drop
        sql_statement = f"CREATE TABLE {temp_table_name} AS SELECT {column_names_str} FROM {table_name}"
        cursor.execute(sql_statement)

        # Drop the original table
        sql_statement = f"DROP TABLE {table_name}"
        cursor.execute(sql_statement)

        # Rename the temporary table to the original table name
        sql_statement = f"ALTER TABLE {temp_table_name} RENAME TO {table_name}"
        cursor.execute(sql_statement)

        # Commit the changes and close the connection
        self.db_connection.commit()

        self.close_connection()

    def executeAndCommit(self, sql_statement: str):
        self.open_connection()

        cursor = self.db_connection.cursor()
        cursor.execute(sql_statement)
        self.db_connection.commit()

        self.close_connection()

    def fetch_all(self, query: str):
        self.open_connection()

        cursor = self.db_connection.cursor()
        cursor.execute(query)
        fetch_all = cursor.fetchall()

        self.close_connection()

        return fetch_all

    def fetch_one_row(self, query: str):
        self.open_connection()
        cursor = self.db_connection.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        self.close_connection()

        return row

    def fetch_one_value(self, query: str) -> Any:
        row = self.fetch_one_row(query)
        if row:
            value = row[0]  # Accessing the first element of the tuple
        else:
            value = None  # In case no results are returned

        return value

    def fetch_one_value_decimal(self, query: str) -> Decimal:
        row = self.fetch_one_row(query)
        if row:
            value = row[0]  # Accessing the first element of the tuple
        else:
            value = 0  # In case no results are returned

        return Decimal(value)

    def fetch_one_value_float(self, query:str) -> float:
        row = self.fetch_one_row(query)
        if row:
            value = row[0]  # Accessing the first element of the tuple
        else:
            value = 0  # In case no results are returned

        return float(value)

    def get_column_info(self, table_name:str, column_name:str):
        table_info = self.get_table_info(table_name)
        column_info = None
        for column in table_info:
            if column[1] == column_name:
                column_info = column

        return column_info

    def get_how_many(self, table_name:str, where:Optional[str]=None)-> int:
        self.open_connection()
        query = f"""
SELECT COUNT(*)
FROM {table_name}

"""

        if where:
            query += where

        how_many = self.fetch_one_value(query)

        self.close_connection()

        return how_many

    def get_table_info(self, table_name: str)-> list[Any]:
        query = f"PRAGMA table_info('{table_name}')"
        self.open_connection()

        cursor = self.db_connection.cursor()
        cursor.execute(query)
        table_info = cursor.fetchall()

        self.close_connection()

        return table_info

    def open_connection(self):
        # Connect to SQLite database
        self.db_connection = sqlite3.connect(self.db_path)

    def rename_column(self, table_name:str, old_column_name:str, new_column_name:str):        

        self.open_connection()

        cursor = self.db_connection.cursor()

        # Get the table structure
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

        # Create a list of column names with the renamed column

        new_column_phrase = f"{old_column_name} AS {new_column_name}"

        new_columns = [
            (f'"{col[1]}"' if col[1] != old_column_name else new_column_phrase)
            for col in columns
        ]
        new_columns_str = ", ".join(new_columns)

        # Create a new table with the renamed column
        sql_statement = f"CREATE TABLE temp_{table_name} AS SELECT {new_columns_str} FROM {table_name}"
        cursor.execute(sql_statement)

        # Drop the original table
        sql_statement = f"DROP TABLE {table_name}"
        cursor.execute(sql_statement)

        # Rename the new table to the original table name
        sql_statement = f"ALTER TABLE temp_{table_name} RENAME TO {table_name}"
        cursor.execute(sql_statement)

        # Commit the changes and close the connection
        self.db_connection.commit()

        self.close_connection()

    def text_to_real(self, table_name:str, column_name:str):
        table_info = self.get_table_info(table_name)

        column_type = None

        for column in table_info:
            if column[1] == column_name:
                column_type = column[2]

        if column_type == "TEXT":
            sql_statements = [
                f"ALTER TABLE {table_name} ADD COLUMN {column_name}_real REAL",
                f"UPDATE {table_name} SET {column_name}_real = CAST(REPLACE(REPLACE(REPLACE({column_name}, '£', ''), ',', ''), ' ', '') AS REAL)",
            ]
            for sql_statement in sql_statements:
                self.executeAndCommit(sql_statement)

            self.drop_column(table_name, column_name)
            self.rename_column(table_name, f"{column_name}_real", column_name)

from typing import Any
from our_finances.classes.sqlite_helper import SQLiteHelper
from our_finances.classes.query_builder import QueryBuilder


class SQLiteTable:
    def __init__(self, table_name:str)-> None:
        self.sql = SQLiteHelper()
        self.table_name = table_name

    def fetch_all(self)-> list[Any]:
        query = f"SELECT * FROM {self.table_name}"
        return self.sql.fetch_all(query)

    def get_how_many(self)-> int:
        return self.sql.get_how_many(self.table_name)

    def query_builder(self)-> QueryBuilder:
        return QueryBuilder(self.table_name)

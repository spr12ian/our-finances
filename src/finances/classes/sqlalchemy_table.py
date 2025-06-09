from typing import Any

from finances.classes.query_builder import QueryBuilder
from finances.classes.sqlalchemy_helper import (
    SQLAlchemyHelper,
    validate_sqlalchemy_name,
)


class SQLiteTable:
    def __init__(self, table_name: str)->None:
        validate_sqlalchemy_name(table_name)
        self.sql = SQLAlchemyHelper()
        self.table_name = table_name

    def fetch_all(self) -> Any:
        query = f"SELECT * FROM {self.table_name}"
        return self.sql.fetch_all(query)

    def get_how_many(self) -> Any:
        return self.sql.get_how_many(self.table_name)

    def query_builder(self) -> QueryBuilder:
        return QueryBuilder(self.table_name)

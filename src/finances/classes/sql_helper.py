from typing import Any


class SQL_Helper:
    def select_sql_helper(self, preferred_helper: str) -> Any:
        match preferred_helper:
            case "SQLAlchemy":
                from sqlalchemy_helper import SQLAlchemyHelper

                return SQLAlchemyHelper()
            case "SQLite":
                from finances.classes.sqlite_helper import SQLiteHelper

                return SQLiteHelper()
            case _:
                raise ValueError(f"Unexpected preferred_helper: {preferred_helper}")

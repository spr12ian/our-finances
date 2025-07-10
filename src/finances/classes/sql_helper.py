from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from finances.classes.sqlalchemy_helper import SQLAlchemyHelper
    from finances.classes.sqlite_helper import SQLiteHelper

    SQLHelperType = SQLAlchemyHelper | SQLiteHelper
else:
    SQLHelperType = object  # Fallback to satisfy runtime typing

class SQLHelperError(Exception):
    pass


class SQLHelper:
    def select_sql_helper(self, preferred_helper: str) -> SQLHelperType:
        match preferred_helper:
            case "SQLAlchemy":
                from finances.classes.sqlalchemy_helper import SQLAlchemyHelper

                return SQLAlchemyHelper()
            case "SQLite":
                from finances.classes.sqlite_helper import SQLiteHelper

                return SQLiteHelper()
            case _:
                raise SQLHelperError(
                    f"Unexpected preferred_helper: {preferred_helper}"
                ) from ValueError

import importlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from finances.classes.sqlalchemy_helper import SQLAlchemyHelper
    from finances.classes.sqlite_helper import SQLiteHelper

    SQLHelperType = SQLAlchemyHelper | SQLiteHelper
else:
    SQLHelperType = object  # Fallback to satisfy runtime typing


class SQLHelperError(Exception):
    pass


mapping = {
    "SQLAlchemy": "finances.classes.sqlalchemy_helper.SQLAlchemyHelper",
    "SQLite": "finances.classes.sqlite_helper.SQLiteHelper",
}


def select_sql_helper(preferred_helper: str) -> SQLHelperType:
    try:
        module_path, class_name = mapping[preferred_helper].rsplit(".", 1)
        mod = importlib.import_module(module_path)
        return getattr(mod, class_name)()
    except KeyError:
        raise SQLHelperError(
            f"Unexpected preferred_helper: {preferred_helper}"
        ) from KeyError

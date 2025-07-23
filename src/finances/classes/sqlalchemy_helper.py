# standard imports
from collections.abc import Sequence
from typing import Any, cast

# pip imports
from sqlalchemy import Row, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

# local imports
from finances.classes.config import Config
from finances.util.string_helpers import to_method_name


class SQLAlchemyHelper:
    def __init__(self) -> None:
        self.read_config()

        self.engine = create_engine(self.database_url, echo=self.is_echo_enabled)
        self.Session = sessionmaker(bind=self.engine)

    def drop_column(self, table_name: str, column_name: str) -> None:
        session = self.Session()
        try:
            # Step 1: get current schema
            result = session.execute(text(f"PRAGMA table_info({table_name})"))
            columns_info = result.fetchall()

            # Step 2: build list of columns to keep
            keep_columns = [col[1] for col in columns_info if col[1] != column_name]
            if column_name not in [col[1] for col in columns_info]:
                raise ValueError(
                    f"Column {column_name} not found in table {table_name}"
                )

            # Step 3: create new table using selected columns
            tmp_table = f"{table_name}_tmp"
            create_table_statement = (
                f"CREATE TABLE {tmp_table} AS "
                f"SELECT {', '.join(keep_columns)} "
                f"FROM {table_name}"
            )
            session.execute(text(create_table_statement))

            # Step 4: replace original table
            session.execute(text(f"DROP TABLE {table_name}"))
            session.execute(text(f"ALTER TABLE {tmp_table} RENAME TO {table_name}"))
            session.commit()
        finally:
            session.close()

    def executeAndCommit(self, sql: str) -> None:
        session = self.Session()
        try:
            session.execute(text(sql))
            session.commit()
        finally:
            session.close()

    def fetch_all(self, query: str) -> list[Any]:
        text_clause = text(query)
        session = self.Session()
        try:
            # Execute the query
            result = session.execute(text_clause)
            all = result.fetchall()
        finally:
            # Close the session
            session.close()

        return cast(list[Any], all)

    def fetch_one_value(self, query: str) -> Any:
        text_clause = text(query)

        # Open a session
        session = self.Session()
        try:
            # Execute the query
            result = session.execute(text_clause)
            value = result.scalar()
        finally:
            # Close the session
            session.close()

        return value

    def get_db_filename(self) -> Any:
        return self.engine.url.database

    def get_session(self) -> Any:
        return Session(self.engine)

    def get_table_info(self, table_name: str) -> Sequence[Row[Any]]:
        text_clause = text(f"PRAGMA table_info('{table_name}')")

        # Open a session
        session = self.Session()
        try:
            # Execute the query
            result = session.execute(text_clause)
            table_info = result.fetchall()
        finally:
            # Close the session
            session.close()

        return table_info

    def read_config(self) -> None:
        config = Config()

        database_url = config.get("OUR_FINANCES_SQLITE_DB_NAME")
        if not database_url:
            raise ValueError(
                "OUR_FINANCES_SQLITE_DB_NAME is not set in the configuration."
            )
        self.database_url = database_url

        is_echo_enabled = config.get("OUR_FINANCES_SQLITE_ECHO_ENABLED")
        if not is_echo_enabled:
            raise ValueError(
                "OUR_FINANCES_SQLITE_ECHO_ENABLED is not set in the configuration."
            )
        self.is_echo_enabled = is_echo_enabled

    def rename_column(self, table_name: str, old_name: str, new_name: str) -> None:
        session = self.Session()
        try:
            # Step 1: get table structure
            result = session.execute(text(f"PRAGMA table_info({table_name})"))
            columns_info = result.fetchall()

            if old_name not in [col[1] for col in columns_info]:
                raise ValueError(f"Column {old_name} not found in table {table_name}")

            # Step 2: reconstruct schema with new column name
            new_columns: list[str] = []
            select_columns: list[str] = []
            for col in columns_info:
                col_name, col_type = col[1], col[2]
                if col_name == old_name:
                    new_columns.append(f"{new_name} {col_type}")
                    select_columns.append(f"{old_name} AS {new_name}")
                else:
                    new_columns.append(f"{col_name} {col_type}")
                    select_columns.append(col_name)

            tmp_table = f"{table_name}_tmp"
            session.execute(
                text(f"CREATE TABLE {tmp_table} ({', '.join(new_columns)})")
            )
            insert_statement = (
                f"INSERT INTO {tmp_table} "
                f"SELECT {', '.join(select_columns)} "
                f"FROM {table_name}"
            )
            session.execute(text(insert_statement))

            # Step 3: replace original table
            session.execute(text(f"DROP TABLE {table_name}"))
            session.execute(text(f"ALTER TABLE {tmp_table} RENAME TO {table_name}"))
            session.commit()
        finally:
            session.close()

    def text_to_real(self, table_name: str, column_name: str) -> None:
        table_info = self.get_table_info(table_name)

        column_type = None

        for column in table_info:
            if column[1] == column_name:
                column_type = column[2]

        if column_type == "TEXT":
            update_statement = (
                f"UPDATE {table_name} "
                f"SET {column_name}_real = CAST("
                f"REPLACE(REPLACE(REPLACE({column_name}, '£', ''), ',', ''), ' ', '') "
                f"AS REAL)"
            )

            sql_statements = [
                f"ALTER TABLE {table_name} ADD COLUMN {column_name}_real REAL",
                update_statement,
            ]
            for sql_statement in sql_statements:
                self.executeAndCommit(sql_statement)

            self.drop_column(table_name, column_name)
            self.rename_column(table_name, f"{column_name}_real", column_name)


def to_column_name(name: str) -> str:
    valid_method_name = to_method_name(name)

    return valid_method_name


def to_table_name(name: str) -> str:
    valid_method_name = to_method_name(name)

    return valid_method_name


def validate_column_name(name: str) -> None:
    if name != to_column_name(name):
        raise ValueError(f"Invalid column name: {name}")


def validate_table_name(name: str) -> None:
    if name != to_table_name(name):
        raise ValueError(f"Invalid table name: {name}")


# print(len(metadata.tables))
# for table in metadata.tables.values():
#     print(table.name)

#     if not table.primary_key.columns:
#         # Add a primary key manually
#         table.append_column(Column('id', Integer, primary_key=True))

#     for column in table.columns.values():
#         print(f'    {column.name}')


# def examine_model(model):
#     result = session.query(model).all()

#     # Print the actual data contained in the objects
#     for row in result:
#         for column in model.__table__.columns:
#             print(f"{column.name}: {getattr(row, column.name)}")


# model = Base.classes["account_balances"]
# examine_model(model)

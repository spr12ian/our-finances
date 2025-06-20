# standard imports
from typing import Any, Sequence

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

    def text_to_real(self, table_name: str, column_name: str) -> None:
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


def to_sqlalchemy_name(name: str) -> str:
    valid_method_name = to_method_name(name)

    return valid_method_name


def validate_sqlalchemy_name(name: str) -> None:
    if name != to_sqlalchemy_name(name):
        raise ValueError(f"Invalid SQLAlchemy name: {name}")


def clean_column_names(df):
    df.columns = [to_sqlalchemy_name(col) for col in df.columns]
    return df


# print(len(metadata.tables))
# for table in metadata.tables.values():
#     print(table.name)

#     if not table.primary_key.columns:
#         table.append_column(Column('id', Integer, primary_key=True))  # Add a primary key manually

#     for column in table.columns.values():
#         print(f'    {column.name}')


# def examine_model(model):
#     result = session.query(model).all()

#     # Print the actual data contained in the objects
#     for row in result:
#         print({column.name: getattr(row, column.name) for column in model.__table__.columns})


# model = Base.classes["account_balances"]
# examine_model(model)

# standard imports

# pip imports
from our_finances.util.string_helpers import to_valid_method_name
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

# local imports
from finances.classes.config import Config


class SQLAlchemyHelper:
    def __init__(self):
        database_url, is_echo_enabled = self.read_config()

        self.engine = create_engine(database_url, echo=is_echo_enabled)
        self.Session = sessionmaker(bind=self.engine)

    def read_config(self):
        config = Config()

        return config.SQLAlchemy.database_url, config.SQLAlchemy.echo

    def fetch_one_value(self, query):
        query = text(query)

        # Open a session
        session = self.Session()
        try:
            # Execute the query
            result = session.execute(query)
            value = result.scalar()
        finally:
            # Close the session
            session.close()

        return value

    def get_db_filename(self):
        return self.engine.url.database

    def get_session(self):
        return Session(self.engine)

    def get_table_info(self, table_name):
        query = text(f"PRAGMA table_info('{table_name}')")

        # Open a session
        session = self.Session()
        try:
            # Execute the query
            result = session.execute(query)
            table_info = result.fetchall()
        finally:
            # Close the session
            session.close()

        return table_info

    def text_to_real(self, table_name, column_name):
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


def valid_sqlalchemy_name(name: str) -> str:
    valid_method_name = to_valid_method_name(name)

    return valid_method_name


def validate_sqlalchemy_name(name: str) -> None:
    if name != valid_sqlalchemy_name(name):
        raise ValueError(f"Invalid SQLAlchemy name: {name}")


def clean_column_names(df):

    df.columns = [valid_sqlalchemy_name(col) for col in df.columns]
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

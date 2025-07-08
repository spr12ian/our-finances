import os
from pathlib import Path

from sqlalchemy import text

from finances.classes.sqlalchemy_helper import SQLAlchemyHelper

# import sys


def get_file_size(file_path: Path) -> int:
    return os.path.getsize(file_path)


def vacuum_database() -> None:
    alchemy = SQLAlchemyHelper()
    db_file_path = alchemy.get_db_filename()
    print(f"Database file path: {db_file_path}")

    vacuum_statement = text("VACUUM;")

    session = alchemy.get_session()

    try:
        # Print the size of the database file before vacuuming
        before_size = get_file_size(db_file_path)
        print(f"Database size before vacuuming: {before_size} bytes")

        # Execute VACUUM command
        session.execute(vacuum_statement)
        session.commit()

        # Print the size of the database file after vacuuming
        after_size = get_file_size(db_file_path)
        print(f"Database size after vacuuming: {after_size} bytes")

    except Exception as e:
        session.rollback()
    finally:
        # Close the session
        session.close()

    print("Database has been vacuumed")


def main() -> None:
    vacuum_database()


if __name__ == "__main__":
    main()

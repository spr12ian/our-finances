from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy_helper import SQLAlchemyHelper
from our_finances.classes.log_helper import LogHelper
from our_finances.classes.log_helper import debug_function_call
import os

# import sys

l = LogHelper(__file__)
# l.set_level_debug()
l.debug(__file__)


def get_file_size(file_path):
    return os.path.getsize(file_path)


@debug_function_call
def vacuum_database():
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
        l.error(f"An error occurred: {e}")
        session.rollback()
    finally:
        # Close the session
        session.close()

    print("Database has been vacuumed")


def main():
    # # Check if the correct number of arguments is provided
    # print(len(sys.argv))
    # if len(sys.argv) != 2:
    #     print('Usage: pwl vacuum "database_file"')
    #     sys.exit(1)

    # # Get the command line arguments
    # args = sys.argv[1:]  # Exclude the script name

    # db_file_path = args[0]

    vacuum_database()


if __name__ == "__main__":
    main()

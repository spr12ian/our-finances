"""
Test module for SQLAlchemyHelper class.
Tests use a temporary SQLite database to validate core functionality.
"""

import os
import tempfile
from collections.abc import Generator

import pytest
from sqlalchemy import create_engine, text

# Import the class under test
from finances.classes.sqlalchemy_helper import (
    SQLAlchemyHelper,
    validate_table_name,
)


@pytest.fixture(scope="module")
def sqlite_env() -> Generator[str, None, None]:
    """Fixture to set up a temporary SQLite DB and environment variables."""
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".sqlite3")
    db_path = tmp_file.name
    tmp_file.close()

    os.environ["OUR_FINANCES_SQLITE_DB_NAME"] = f"sqlite:///{db_path}"
    os.environ["OUR_FINANCES_SQLITE_ECHO_ENABLED"] = "False"

    engine = create_engine(os.environ["OUR_FINANCES_SQLITE_DB_NAME"])
    with engine.connect() as conn:
        conn.execute(
            text("CREATE TABLE test_table (id INTEGER PRIMARY KEY, amount TEXT);")
        )
        conn.execute(
            text("INSERT INTO test_table (amount) VALUES ('£1,000.00'), ('£2,000.00')")
        )

    yield db_path

    os.remove(db_path)


@pytest.fixture
def helper(sqlite_env: str) -> SQLAlchemyHelper:
    """Fixture that returns a fresh instance of SQLAlchemyHelper."""
    return SQLAlchemyHelper()


def test_get_table_info(helper: SQLAlchemyHelper) -> None:
    """Ensure PRAGMA table_info fetches expected schema."""
    info = helper.get_table_info("test_table")
    assert any(col[1] == "amount" for col in info)


def test_text_to_real(helper: SQLAlchemyHelper) -> None:
    """Convert TEXT column with currency symbols into REAL numeric type."""
    helper.text_to_real("test_table", "amount")
    info = helper.get_table_info("test_table")
    assert "amount" in [col[1] for col in info]
    assert any(col[2] == "REAL" for col in info if col[1] == "amount")


def test_rename_column(helper: SQLAlchemyHelper) -> None:
    """Rename a column and validate new name appears in schema."""
    helper.rename_column("test_table", "amount", "renamed_amount")
    info = helper.get_table_info("test_table")
    assert "renamed_amount" in [col[1] for col in info]


def test_drop_column(helper: SQLAlchemyHelper) -> None:
    """Drop a column and ensure it no longer appears."""
    helper.drop_column("test_table", "renamed_amount")
    info = helper.get_table_info("test_table")
    assert "renamed_amount" not in [col[1] for col in info]


def test_execute_and_commit(helper: SQLAlchemyHelper) -> None:
    """Insert a row using raw SQL and ensure it's committed."""
    helper.executeAndCommit("INSERT INTO test_table (id) VALUES (99)")
    count = helper.fetch_one_value("SELECT COUNT(*) FROM test_table")
    assert isinstance(count, int)
    assert count >= 1


def test_fetch_one_value(helper: SQLAlchemyHelper) -> None:
    """Fetch a single value from the DB."""
    result = helper.fetch_one_value("SELECT 42")
    assert result == 42


def test_get_db_filename(helper: SQLAlchemyHelper, sqlite_env: str) -> None:
    """Verify DB filename is returned correctly."""
    assert helper.get_db_filename() == sqlite_env


def test_get_session(helper: SQLAlchemyHelper) -> None:
    """Validate a session can be opened and closed."""
    session = helper.get_session()
    assert session is not None
    session.close()


def test_validate_sqlalchemy_name_valid() -> None:
    """Check that valid SQLAlchemy names pass validation."""
    validate_table_name("valid_name")


def test_validate_sqlalchemy_name_invalid() -> None:
    """Ensure invalid names raise ValueError."""
    with pytest.raises(ValueError):
        validate_table_name("invalid name")

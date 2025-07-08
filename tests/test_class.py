import pytest

import scripts.download_sheets_to_sqlite as download_sheets_to_sqlite
import scripts.key_check as key_check


def f() -> None:
    raise SystemExit(1)


def func(x: int) -> int:
    return x + 1


def test_answer() -> None:
    assert func(3) == 4


def test_database_to_spreadsheet() -> None:
    # database_to_spreadsheet.main()
    return


def test_key_check() -> None:
    key_check.main()


def test_mytest() -> None:
    with pytest.raises(SystemExit):
        f()


def test_one() -> None:
    x = "this"
    assert "h" in x


def test_spreadsheet_to_database() -> None:
    download_sheets_to_sqlite.main()


def test_two() -> None:
    x = "hello"
    assert hasattr(x, "check")

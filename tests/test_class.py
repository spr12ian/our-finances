import pytest
import scripts.key_check as key_check

import scripts.download_sheets_to_sqlite as download_sheets_to_sqlite


def f():
    raise SystemExit(1)


def func(x):
    return x + 1


def test_answer():
    assert func(3) == 4


def test_database_to_spreadsheet():
    # database_to_spreadsheet.main()
    return


def test_key_check():
    key_check.main()


def test_mytest():
    with pytest.raises(SystemExit):
        f()


def test_one():
    x = "this"
    assert "h" in x


def test_spreadsheet_to_database():
    download_sheets_to_sqlite.main()


def test_two():
    x = "hello"
    assert hasattr(x, "check")

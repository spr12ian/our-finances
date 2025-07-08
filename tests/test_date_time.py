from finances.classes.date_time_helper import DateTimeHelper


def test_uk_to_iso() -> None:
    d = DateTimeHelper()
    assert d.ISO_to_UK("2025-06-09") == "09/06/2025"
    assert d.UK_to_ISO("09/06/2025") == "2025-06-09"

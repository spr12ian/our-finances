from __future__ import annotations

from collections.abc import Generator
from unittest.mock import MagicMock

import pytest

from finances.classes.gbp import GBP
from finances.classes.sqlite_table.hmrc_people_details import HMRCPeopleDetails


@pytest.fixture
def mock_table() -> Generator[HMRCPeopleDetails, None, None]:
    table = HMRCPeopleDetails("ABC123")
    table.sql = MagicMock()
    mock_builder = MagicMock()
    mock_builder.select = lambda col: mock_builder
    mock_builder.where = lambda clause: mock_builder
    mock_builder.build = lambda: "SQL QUERY"
    table.query_builder = MagicMock(return_value=mock_builder)
    yield table


def test_are_nics_needed_to_achieve_max_state_pension_yes(
    mock_table: HMRCPeopleDetails,
) -> None:
    mock_table.sql.fetch_one_value.return_value = "Yes"
    assert mock_table.are_nics_needed_to_achieve_max_state_pension() is True


def test_are_nics_needed_to_achieve_max_state_pension_no(
    mock_table: HMRCPeopleDetails,
) -> None:
    mock_table.sql.fetch_one_value.return_value = "No"
    assert mock_table.are_nics_needed_to_achieve_max_state_pension() is False


@pytest.mark.parametrize(
    "column,expected",
    [
        ("marital_status", "Married"),
        ("marriage_date", "2020-01-01"),
        ("nino", "AA123456A"),
        ("refunds_to", "HMRC"),
        ("spouse_code", "XYZ789"),
        ("taxpayer_residency_status", "UK"),
        ("utr", "1234567890"),
        ("utr_check_digit", "7"),
        ("receives_child_benefit", "Yes"),
        ("weekly_state_pension_forecast", "185.15"),
    ],
)
def test_get_value_by_column(
    mock_table: HMRCPeopleDetails, column: str, expected: str
) -> None:
    mock_table.sql.fetch_one_value.return_value = expected

    if column == "receives_child_benefit":
        assert mock_table.receives_child_benefit() is True
    elif column == "weekly_state_pension_forecast":
        forecast: GBP = mock_table.get_weekly_state_pension_forecast()
        assert isinstance(forecast, GBP)
        assert str(forecast) == f"£{Decimal(expected):.2f}"
    else:
        method = getattr(mock_table, f"get_{column}", None)
        if method:
            result: str | None = method()
            assert result == expected


def test_get_utr_check_digit_empty(mock_table: HMRCPeopleDetails) -> None:
    mock_table.sql.fetch_one_value.return_value = None
    assert mock_table.get_utr_check_digit() == ""


def test_is_married_true(mock_table: HMRCPeopleDetails) -> None:
    mock_table.sql.fetch_one_value.return_value = "Married"
    assert mock_table.is_married() is True


def test_is_married_false(mock_table: HMRCPeopleDetails) -> None:
    mock_table.sql.fetch_one_value.return_value = "Single"
    assert mock_table.is_married() is False


def test_get_uk_marriage_date_none(mock_table: HMRCPeopleDetails) -> None:
    mock_table.get_marriage_date = MagicMock(return_value=None)
    result: str | None = mock_table.get_uk_marriage_date()
    assert result is None


def test_get_uk_marriage_date_formatted(mock_table: HMRCPeopleDetails) -> None:
    mock_table.get_marriage_date = MagicMock(return_value="2020-12-25")

    from finances.classes.date_time_helper import DateTimeHelper

    original_method = DateTimeHelper.ISO_to_UK
    DateTimeHelper.ISO_to_UK = lambda self, x: "25/12/2020"  # type: ignore[assignment]

    try:
        result: str | None = mock_table.get_uk_marriage_date()
        assert result == "25/12/2020"
    finally:
        DateTimeHelper.ISO_to_UK = original_method


def test_fetch_by_code(mock_table: HMRCPeopleDetails) -> None:
    expected_result: list[dict[str, str]] = [{"code": "ABC123", "nino": "QQ123456C"}]
    mock_table.sql.fetch_all.return_value = expected_result
    result: list[dict[str, str]] = mock_table.fetch_by_code("ABC123")
    assert result == expected_result

from collections.abc import Callable, Sequence
from functools import cached_property
from typing import Any, TypeVar

from finances.classes.percentage import Percentage
from finances.classes.sqlite_helper import to_table_name
from finances.classes.sqlite_table import SQLiteTable
from finances.util.string_helpers import label_to_attr

T = TypeVar("T")  # The return type of the bound property


def bind_constants(
    labels: Sequence[str], *, return_type: type[T], resolver: Callable[[Any, str], T]
) -> Callable[[type], type]:
    """
    Create @cached_property attributes from a list of labels.

    Args:
        labels: List of human-readable labels (e.g., from a spreadsheet or db)
        return_type: The return type (used for __annotations__)
        resolver: Function taking (self, label) -> T

    Example:
        @bind_constants(
            ["Basic tax rate", "Higher tax rate"],
            return_type=Percentage,
            resolver=lambda self, label: self._lookup(label),
        )
        class Rates: ...
    """

    def decorator(cls: type) -> type:
        cls.__annotations__ = dict(getattr(cls, "__annotations__", {}))

        for label in labels:
            attr_name = label_to_attr(label)
            cls.__annotations__[attr_name] = return_type

            @cached_property
            def prop(self, label=label):  # noqa: ANN001
                return resolver(self, label)

            prop.__doc__ = f"Dynamically bound constant for '{label}'"
            setattr(cls, attr_name, prop)

        return cls

    return decorator


@bind_constants(
    [
        "Additional tax rate",
        "Basic tax rate",
        "NIC Class 4 lower rate",
        "NIC Class 4 upper rate",
        "Dividends basic rate",
        "Higher tax rate",
        "Savings basic rate",
    ],
    return_type=Percentage,
    resolver=lambda self, label: self._get_value_by_hmrc_constant(label),
)
class HMRC_ConstantPercentagesByYear(SQLiteTable):
    def __init__(self, tax_year: str) -> None:
        super().__init__("hmrc_constant_percentages_by_year")
        self.tax_year = tax_year
        self.tax_year_col = to_table_name(tax_year)

    def _get_value_by_hmrc_constant(self, hmrc_constant: str) -> Percentage:
        tax_year = self.tax_year
        tax_year_col = self.tax_year_col
        query = (
            self.query_builder()
            .select(tax_year_col)
            .where(f'"hmrc_constant" = "{hmrc_constant}"')
            .build()
        )
        result = self.sql.fetch_one_value(
            query
        )  # Could be formatted as a float, a ccy, etc.

        if result is None:
            raise ValueError(
                f"Could not find the HMRC constant '{hmrc_constant}' for {tax_year}"
            )

        return Percentage(result)

from decimal import Decimal
from functools import total_ordering
from typing import Any

from finances.classes.rounding import Rounding


class GBPError(Exception):
    pass


MONEY = Decimal | int | float | str | None


@total_ordering
class GBP:
    def __init__(self, amount: MONEY = 0, *, rounding: str = Rounding.HALF_UP) -> None:
        if not Rounding.is_valid(rounding):
            raise GBPError(f"Invalid rounding mode: {rounding}") from ValueError
        if amount is None:
            amount = 0
        if isinstance(amount, float):
            amount = f"{amount:.2f}"
        self._value = Decimal(amount).quantize(Decimal("0.01"), rounding=rounding)

    # ---------- internal ----------
    @staticmethod
    def _to_decimal(other: Any) -> Decimal | None:
        """Return a Decimal if *other* can be treated as money, else None."""
        if isinstance(other, GBP):
            return other._value
        try:
            return Decimal(str(other))
        except Exception:  # noqa: BLE001
            return None

    # ---------- equality ----------
    def __eq__(self, other: object) -> bool:  # type: ignore[override]
        other_val = self._to_decimal(other)
        if other_val is None:
            return NotImplemented
        return self._value == other_val

    # ---------- ordering (only __lt__ needed thanks to @total_ordering) ----------
    def __lt__(self, other: MONEY) -> bool:  # type: ignore[override]
        other_val = self._to_decimal(other)
        if other_val is None:
            return NotImplemented
        return self._value < other_val

    # ---------- arithmetic ----------
    def __add__(self, other: MONEY) -> "GBP":
        other_val = self._to_decimal(other)
        if other_val is None:
            return NotImplemented
        return GBP(self._value + other_val)

    def __sub__(self, other: MONEY) -> "GBP":
        other_val = self._to_decimal(other)
        if other_val is None:
            return NotImplemented
        return GBP(self._value - other_val)

    def __format__(self, format_spec: str) -> str:
        return format(str(self), format_spec)

    def __mul__(self, other: MONEY) -> "GBP":
        other_val = self._to_decimal(other)
        if other_val is None:
            return NotImplemented
        return GBP(self._value * other_val)

    def __repr__(self) -> str:
        return f"GBP({str(self)})"

    def __str__(self) -> str:
        return f"£{self._value:.2f}"

    def __truediv__(self, other: MONEY) -> "GBP":
        other_val = self._to_decimal(other)
        if other_val is None:
            return NotImplemented
        return GBP(self._value / other_val)

    def __radd__(self, other: MONEY) -> "GBP":
        if other == 0:
            return self
        return self.__add__(other)

    @property
    def value(self) -> Decimal:
        return self._value

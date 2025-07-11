from decimal import Decimal

from finances.classes.gbp import GBP
from finances.classes.rounding import Rounding

PERCENT = Decimal | int | float | str | None


class PercentageError(Exception):
    pass


class Percentage:
    def __init__(
        self, amount: PERCENT = 0, *, rounding: str = Rounding.HALF_UP
    ) -> None:
        if not Rounding.is_valid(rounding):
            raise PercentageError(f"Invalid rounding mode: {rounding}") from ValueError
        if amount is None:
            amount = 0
        if isinstance(amount, float):
            amount = f"{amount:.2f}"
        self._value = Decimal(amount).quantize(Decimal("0.01"), rounding=rounding)

    def __add__(self, other: "Percentage") -> "Percentage":
        if not isinstance(other, Percentage):
            return NotImplemented
        return Percentage(self._value + other._value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Percentage):
            return self._value == other._value
        if isinstance(other, Decimal):
            return self._value == other
        return NotImplemented

    def __format__(self, format_spec: str) -> str:
        return format(str(self), format_spec)

    def __ge__(self, other: "Percentage") -> bool:
        return not self < other

    def __gt__(self, other: "Percentage") -> bool:
        return not self <= other

    def __le__(self, other: "Percentage") -> bool:
        return self == other or self < other

    def __lt__(self, other: "Percentage") -> bool:
        if not isinstance(other, Percentage):
            return NotImplemented
        return self._value < other._value

    def __mul__(self, other: Decimal | int | float) -> "Percentage":
        return Percentage(self._value * Decimal(str(other)))

    def __repr__(self) -> str:
        return f"Percentage({str(self)})"

    def __str__(self) -> str:
        return f"{self._value:.2f}%"

    def __sub__(self, other: "Percentage") -> "Percentage":
        if not isinstance(other, Percentage):
            return NotImplemented
        return Percentage(self._value - other._value)

    def __truediv__(self, other: Decimal | int | float) -> "Percentage":
        return Percentage(self._value / Decimal(str(other)))

    def apply_to(self, value: Decimal | int | float) -> Decimal:
        return Decimal(str(value)) * (self._value / Decimal("100"))

    def apply_to_gbp(self, value: GBP) -> GBP:
        return value * self.as_fraction()

    def as_fraction(self) -> Decimal:
        """Return the percentage as a Decimal between 0 and 1."""
        return self._value / Decimal("100")

    def quantized(self, dp: int = 2) -> Decimal:
        return self._value.quantize(Decimal("1").scaleb(-dp))

    @property
    def value(self) -> Decimal:
        return self._value

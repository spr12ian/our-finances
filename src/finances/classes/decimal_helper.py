from decimal import Decimal, getcontext, ROUND_HALF_UP
from typing import Optional, Union

MONEY = Union[Decimal, int, float]

# Set the global rounding mode
getcontext().rounding = ROUND_HALF_UP


class DecimalHelper:
    def __init__(self, decimal_places: Optional[int] = None):
        self.decimal_places = decimal_places

    def get_decimal(self, value: MONEY) -> Decimal:
        return Decimal(value)

    def get_money(self, value: Decimal) -> Decimal:
        """Ensure all money values are rounded correctly to 2 decimal places."""
        return value.quantize(Decimal("0.01"))

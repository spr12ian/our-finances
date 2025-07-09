from decimal import Decimal

MONEY = Decimal | int | float | str | None


class GBP(Decimal):
    """
    Class to represent a monetary value in GBP (British Pounds).
    """

    def __new__(cls, amount: MONEY = 0.0) -> "GBP":
        if amount is None:
            amount = 0.0
        return super().__new__(cls, amount)

    def __str__(self) -> str:
        return f"£{self:.2f}"

from decimal import Decimal

MONEY = Decimal | int | float | str | None

class GBP(Decimal):
    """
    Class to represent a monetary value in GBP (British Pounds).
    """

    def __init__(self, amount: MONEY)-> None:
        if amount is None:
            amount = 0.0
        self.amount = Decimal(amount)

    def __str__(self)-> str:
        return f"£{self.amount:.2f}"

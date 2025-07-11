from functools import cached_property

from beartype import beartype

from finances.classes.gbp import GBP
from finances.classes.percentage import Percentage
from finances.classes.sqlite_table.hmrc_constants_by_year import HMRCConstantsByYear


class HMRCTax:
    def __init__(self, tax_year: str) -> None:
        self._constants = HMRCConstantsByYear(tax_year)

    @cached_property
    def constants(self) -> HMRCConstantsByYear:
        return self._constants

    @cached_property
    def dividends_allowance(self) -> GBP:
        return GBP(self.constants.dividends_allowance)

    @cached_property
    def dividends_basic_rate(self) -> Percentage:
        return Percentage(
            self.constants.dividends_basic_rate
        )  # 8.75% from 2024 to 2025

    @beartype
    def calculate_dividends_tax(
        self, amount: GBP, available_allowance: GBP = GBP(0)
    ) -> tuple[GBP, GBP]:
        if amount <= available_allowance:
            tax = GBP(0)
            remaining = available_allowance - amount
        else:
            taxable = amount - available_allowance
            remaining = GBP(0)

            if taxable <= self.dividends_allowance:
                tax = GBP(0)
            else:
                taxable = taxable - self.dividends_allowance
                rate = self.dividends_basic_rate
                tax = rate.apply_to_gbp(taxable)

        return tax, remaining

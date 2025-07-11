from decimal import Decimal
from functools import cached_property

from finances.classes.percentage import Percentage
from finances.classes.sqlite_helper import to_table_name
from finances.classes.sqlite_table import SQLiteTable
from finances.classes.sqlite_table.hmrc_constant_amounts_by_year import (
    HMRC_ConstantAmountsByYear,
)
from finances.classes.sqlite_table.hmrc_constant_percentages_by_year import (
    HMRC_ConstantPercentagesByYear,
)


class HMRCConstantsByYearError(Exception):
    pass


class HMRCConstantsByYear(SQLiteTable):
    def __init__(self, tax_year: str) -> None:
        super().__init__("hmrc_constants_by_year")
        self.tax_year = tax_year
        self.tax_year_col = to_table_name(tax_year)
        self.amount_constants = HMRC_ConstantAmountsByYear(tax_year)
        self.percentage_constants = HMRC_ConstantPercentagesByYear(tax_year)

    def _get_value_by_hmrc_constant(self, hmrc_constant: str) -> int:
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
            raise HMRCConstantsByYearError(
                f"Could not find the HMRC constant '{hmrc_constant}' for {tax_year}"
            )

        return int(result)

    @cached_property
    def additional_rate_threshold(self) -> Decimal:
        return self.amount_constants.get_additional_rate_threshold()

    @cached_property
    def additional_tax_rate(self) -> Percentage:
        return self.percentage_constants.additional_tax_rate

    @cached_property
    def basic_rate_threshold(self) -> Decimal:
        return self.amount_constants.get_basic_rate_threshold()

    @cached_property
    def basic_tax_rate(self) -> Percentage:
        return self.percentage_constants.basic_tax_rate

    @cached_property
    def class_2_annual_amount(self) -> Decimal:
        class_2_nics_weekly_rate = self.class_2_weekly_rate
        how_many_nic_weeks_in_year = self.how_many_nic_weeks_in_year

        class_2_annual_amount = how_many_nic_weeks_in_year * class_2_nics_weekly_rate

        return class_2_annual_amount

    @cached_property
    def class_2_weekly_rate(self) -> Decimal:
        return self.amount_constants.get_class_2_weekly_rate()

    @cached_property
    def class_4_lower_profits_limit(self) -> Decimal:
        return self.amount_constants.get_class_4_lower_profits_limit()

    @cached_property
    def class_4_lower_rate(self) -> Decimal:
        return self.percentage_constants.get_class_4_lower_rate()

    @cached_property
    def class_4_upper_profits_limit(self) -> Decimal:
        return self.amount_constants.get_class_4_upper_profits_limit()

    @cached_property
    def class_4_upper_rate(self) -> Decimal:
        return self.percentage_constants.get_class_4_upper_rate()

    @cached_property
    def dividends_allowance(self) -> Decimal:
        return self.amount_constants.get_dividends_allowance()

    @cached_property
    def dividends_basic_rate(self) -> Decimal:
        return self.percentage_constants.get_dividends_basic_rate()

    @cached_property
    def higher_rate_threshold(self) -> Decimal:
        return self.amount_constants.get_higher_rate_threshold()

    @cached_property
    def higher_tax_rate(self) -> Decimal:
        return self.percentage_constants.get_higher_tax_rate()

    @cached_property
    def marriage_allowance(self) -> Decimal:
        return self.amount_constants.get_marriage_allowance()

    @cached_property
    def personal_allowance(self) -> Decimal:
        return self.amount_constants.get_personal_allowance()

    @cached_property
    def personal_savings_allowance(self) -> Decimal:
        return self.amount_constants.get_personal_savings_allowance()

    @cached_property
    def property_income_allowance(self) -> Decimal:
        return self.amount_constants.get_property_income_allowance()

    @cached_property
    def savings_basic_rate(self) -> Decimal:
        return self.percentage_constants.get_savings_basic_rate()

    @cached_property
    def savings_nil_band(self) -> Decimal:
        return self.amount_constants.get_savings_nil_band()

    @cached_property
    def small_profits_threshold(self) -> Decimal:
        return self.amount_constants.get_small_profits_threshold()

    @cached_property
    def starting_rate_limit_for_savings(self) -> Decimal:
        return self.amount_constants.get_starting_rate_limit_for_savings()

    @cached_property
    def trading_income_allowance(self) -> Decimal:
        try:
            trading_income_allowance = (
                self.amount_constants.get_trading_income_allowance()
            )
        except ValueError as v:
            raise HMRCConstantsByYearError(
                "Error in get_trading_income_allowance"
            ) from v

        return trading_income_allowance

    @cached_property
    def vat_registration_threshold(self) -> Decimal:
        return self.amount_constants.get_vat_registration_threshold()

    @cached_property
    def weekly_state_pension(self) -> Decimal:
        return self.amount_constants.get_weekly_state_pension()

    @cached_property
    def how_many_nic_weeks_in_year(self) -> int:
        how_many_nic_weeks_in_year = self._get_value_by_hmrc_constant(
            "How many NIC weeks in year"
        )

        return how_many_nic_weeks_in_year

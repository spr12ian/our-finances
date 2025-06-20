from decimal import Decimal
from functools import cache

from sqlalchemy_helper import to_sqlalchemy_name

from finances.classes.sqlite_table import SQLiteTable


class HMRC_ConstantAmountsByYear(SQLiteTable):
    def _get_value_by_hmrc_constant(self, hmrc_constant: str) -> Decimal:
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
                f"Could not find the HMRC constant '{hmrc_constant}' for tax year {tax_year}"
            )

        return Decimal(result)

    def __init__(self, tax_year):
        self.l.set_level_debug()
        super().__init__("hmrc_constant_amounts_by_year")
        self.tax_year = tax_year
        self.tax_year_col = to_sqlalchemy_name(tax_year)

    @cache
    def get_additional_rate_threshold(self) -> Decimal:
        additional_rate_threshold = self._get_value_by_hmrc_constant(
            "Additional rate threshold"
        )

        return additional_rate_threshold

    @cache
    def get_basic_rate_threshold(self) -> Decimal:
        basic_rate_threshold = self._get_value_by_hmrc_constant("Basic rate threshold")

        return basic_rate_threshold

    @cache
    def get_class_2_weekly_rate(self) -> Decimal:
        class_2_nics_weekly_rate = self._get_value_by_hmrc_constant(
            "NIC Class 2 weekly rate"
        )

        return class_2_nics_weekly_rate

    @cache
    def get_class_4_lower_profits_limit(self) -> Decimal:
        class_4_lower_profits_limit = self._get_value_by_hmrc_constant(
            "NIC Class 4 lower profits limit"
        )

        return class_4_lower_profits_limit

    @cache
    def get_class_4_upper_profits_limit(self) -> Decimal:
        class_4_upper_profits_limit = self._get_value_by_hmrc_constant(
            "NIC Class 4 upper profits limit"
        )

        return class_4_upper_profits_limit

    @cache
    def get_dividends_allowance(self) -> Decimal:
        dividends_allowance = self._get_value_by_hmrc_constant("Dividends allowance")

        return dividends_allowance

    @cache
    def get_higher_rate_threshold(self) -> Decimal:
        higher_rate_threshold = self._get_value_by_hmrc_constant(
            "Higher rate threshold"
        )

        return higher_rate_threshold

    @cache
    def get_marriage_allowance(self) -> Decimal:
        marriage_allowance = self._get_value_by_hmrc_constant("Marriage allowance")

        return marriage_allowance

    @cache
    def get_personal_allowance(self) -> Decimal:
        personal_allowance = self._get_value_by_hmrc_constant("Personal allowance")

        return personal_allowance

    @cache
    def get_personal_savings_allowance(self) -> Decimal:
        personal_savings_allowance = self._get_value_by_hmrc_constant(
            "Personal savings allowance for basic rate taxpayers"
        )

        return personal_savings_allowance

    @cache
    def get_property_income_allowance(self) -> Decimal:
        property_income_allowance = self._get_value_by_hmrc_constant(
            "Property income allowance"
        )

        return property_income_allowance

    @cache
    def get_savings_nil_band(self) -> Decimal:
        savings_nil_band = self._get_value_by_hmrc_constant("Savings nil band")

        return savings_nil_band

    @cache
    def get_small_profits_threshold(self) -> Decimal:
        small_profits_threshold = self._get_value_by_hmrc_constant(
            "NIC Class 2 small profits threshold"
        )

        return small_profits_threshold

    @cache
    def get_starting_rate_limit_for_savings(self) -> Decimal:
        starting_rate_limit_for_savings = self._get_value_by_hmrc_constant(
            "Starting rate limit for savings"
        )
            f"starting_rate_limit_for_savings: {starting_rate_limit_for_savings}"
        )

        return starting_rate_limit_for_savings

    # @lru_cache(maxsize=None)
    def get_trading_income_allowance(self) -> Decimal:
        trading_income_allowance = self._get_value_by_hmrc_constant(
            "Trading income allowance"
        )

        return trading_income_allowance

    @cache
    def get_vat_registration_threshold(self) -> Decimal:
        vat_registration_threshold = self._get_value_by_hmrc_constant(
            "VAT registration threshold"
        )

        return vat_registration_threshold

    @cache
    def get_weekly_state_pension(self) -> Decimal:
        weekly_state_pension = self._get_value_by_hmrc_constant("Weekly state pension")

        return weekly_state_pension

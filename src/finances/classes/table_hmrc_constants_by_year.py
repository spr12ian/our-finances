
from sqlalchemy_helper import valid_sqlalchemy_name
from our_finances.classes.sqlite_table import SQLiteTable
from table_hmrc_constant_amounts_by_year import HMRC_ConstantAmountsByYear
from table_hmrc_constant_percentages_by_year import HMRC_ConstantPercentagesByYear
from decimal import Decimal
from functools import lru_cache


class HMRC_ConstantsByYear(SQLiteTable):

    def __init__(self, tax_year):

        super().__init__("hmrc_constants_by_year")
        self.tax_year = tax_year
        self.tax_year_col = valid_sqlalchemy_name(tax_year)
        self.amount_constants=HMRC_ConstantAmountsByYear(tax_year)
        self.percentage_constants=HMRC_ConstantPercentagesByYear(tax_year)

    def _get_value_by_hmrc_constant(self, hmrc_constant: str) -> int:
        tax_year = self.tax_year
        tax_year_col = self.tax_year_col
        query = (
            self.query_builder()
            .select(tax_year_col)
            .where(f'"hmrc_constant" = "{hmrc_constant}"')
            .build()
        )
        self.l.debug(query)
        result = self.sql.fetch_one_value(
            query
        )  # Could be formatted as a float, a ccy, etc.

        if result is None:
            raise ValueError(
                f"Could not find the HMRC constant '{hmrc_constant}' for tax year {tax_year}"
            )

        return int(result)
    
    @lru_cache(maxsize=None)
    def get_additional_rate_threshold(self) -> Decimal:
        self.l.debug("get_additional_rate_threshold")
        return self.amount_constants.get_additional_rate_threshold()
    
    @lru_cache(maxsize=None)
    def get_additional_tax_rate(self) -> Decimal:
        return self.percentage_constants.get_additional_tax_rate()
    
    @lru_cache(maxsize=None)
    def get_basic_rate_threshold(self) -> Decimal:
        return self.amount_constants.get_basic_rate_threshold()
    
    @lru_cache(maxsize=None)
    def get_basic_tax_rate(self) -> Decimal:
        return self.percentage_constants.get_basic_tax_rate() 

    @lru_cache(maxsize=None)
    def get_class_2_annual_amount(self) -> Decimal:
        class_2_nics_weekly_rate = self.get_class_2_weekly_rate()
        how_many_nic_weeks_in_year = self.how_many_nic_weeks_in_year()

        class_2_annual_amount = how_many_nic_weeks_in_year * class_2_nics_weekly_rate

        self.l.debug(f"class_2_annual_amount: {class_2_annual_amount}")

        return class_2_annual_amount
    
    @lru_cache(maxsize=None)
    def get_class_2_weekly_rate(self) -> Decimal:
        return self.amount_constants.get_class_2_weekly_rate()
    
    @lru_cache(maxsize=None)
    def get_class_4_lower_profits_limit(self) -> Decimal:
        return self.amount_constants.get_class_4_lower_profits_limit()
    
    @lru_cache(maxsize=None)
    def get_class_4_lower_rate(self) -> Decimal:
        return self.percentage_constants.get_class_4_lower_rate()
    
    @lru_cache(maxsize=None)
    def get_class_4_upper_profits_limit(self) -> Decimal:
        return self.amount_constants.get_class_4_upper_profits_limit()
    
    @lru_cache(maxsize=None)
    def get_class_4_upper_rate(self) -> Decimal:
        return self.percentage_constants.get_class_4_upper_rate()
    
    @lru_cache(maxsize=None)
    def get_dividends_allowance(self) -> Decimal:
        return self.amount_constants.get_dividends_allowance()
    
    @lru_cache(maxsize=None)
    def get_dividends_basic_rate(self) -> Decimal:
        return self.percentage_constants.get_dividends_basic_rate()
    
    @lru_cache(maxsize=None)
    def get_higher_rate_threshold(self) -> Decimal:
        return self.amount_constants.get_higher_rate_threshold()
    
    @lru_cache(maxsize=None)
    def get_higher_tax_rate(self) -> Decimal:
        return self.percentage_constants.get_higher_tax_rate()
    
    @lru_cache(maxsize=None)
    def get_marriage_allowance(self) -> Decimal:
        return self.amount_constants.get_marriage_allowance()
    
    @lru_cache(maxsize=None)
    def get_personal_allowance(self) -> Decimal:
        return self.amount_constants.get_personal_allowance()
    
    @lru_cache(maxsize=None)
    def get_personal_savings_allowance(self) -> Decimal:
        return self.amount_constants.get_personal_savings_allowance()
    
    @lru_cache(maxsize=None)
    def get_property_income_allowance(self) -> Decimal:
        return self.amount_constants.get_property_income_allowance()
    
    @lru_cache(maxsize=None)
    def get_savings_basic_rate(self) -> Decimal:
        return self.percentage_constants.get_savings_basic_rate()
    
    @lru_cache(maxsize=None)
    def get_savings_nil_band(self) -> Decimal:
        return self.amount_constants.get_savings_nil_band()
    
    @lru_cache(maxsize=None)
    def get_small_profits_threshold(self) -> Decimal:
        return self.amount_constants.get_small_profits_threshold()
    
    @lru_cache(maxsize=None)
    def get_starting_rate_limit_for_savings(self) -> Decimal:
        return self.amount_constants.get_starting_rate_limit_for_savings()
    
    def get_trading_income_allowance(self) -> Decimal:
        self.l.debug("get_trading_income_allowance")
        try:
            trading_income_allowance = self.amount_constants.get_trading_income_allowance()
            self.l.debug(f"trading_income_allowance: {trading_income_allowance}")
        except ValueError as v:
            self.l.error(f"Error in get_trading_income_allowance: {v}")
            raise
        return trading_income_allowance
    
    @lru_cache(maxsize=None)
    def get_vat_registration_threshold(self) -> Decimal:
        return self.amount_constants.get_vat_registration_threshold()
    
    @lru_cache(maxsize=None)
    def get_weekly_state_pension(self) -> Decimal:
        return self.amount_constants.get_weekly_state_pension()

    @lru_cache(maxsize=None)
    def how_many_nic_weeks_in_year(self) -> int:
        how_many_nic_weeks_in_year = self._get_value_by_hmrc_constant(
            "How many NIC weeks in year"
        )

        self.l.debug(f"how_many_nic_weeks_in_year: {how_many_nic_weeks_in_year}")

        return how_many_nic_weeks_in_year

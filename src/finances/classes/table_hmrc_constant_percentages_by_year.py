from decimal import Decimal
from functools import cache

from sqlalchemy_helper import valid_sqlalchemy_name

from finances.classes.sqlite_table import SQLiteTable


class HMRC_ConstantPercentagesByYear(SQLiteTable):
    def _get_value_by_hmrc_constant(self, hmrc_constant: str) -> Decimal:
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

        return Decimal(result)

    def __init__(self, tax_year):
        self.l = LogHelper("HMRC_ConstantPercentagesByYear")
        self.l.set_level_debug()
        self.l.debug(__file__)
        self.l.debug(f"tax_year: {tax_year}")
        super().__init__("hmrc_constant_percentages_by_year")
        self.tax_year = tax_year
        self.tax_year_col = valid_sqlalchemy_name(tax_year)

    @cache
    def get_additional_tax_rate(self) -> Decimal:
        additional_tax_rate = self._get_value_by_hmrc_constant("Additional tax rate")

        self.l.debug(f"additional_tax_rate: {additional_tax_rate}")

        return additional_tax_rate

    @cache
    def get_basic_tax_rate(self) -> Decimal:
        basic_tax_rate = self._get_value_by_hmrc_constant("Basic tax rate")

        self.l.debug(f"basic_tax_rate: {basic_tax_rate}")

        return basic_tax_rate

    @cache
    def get_class_4_lower_rate(self) -> Decimal:
        class_4_nics_lower_rate = self._get_value_by_hmrc_constant(
            "NIC Class 4 lower rate"
        )

        self.l.debug(f"class_4_nics_lower_rate: {class_4_nics_lower_rate}")

        return class_4_nics_lower_rate

    @cache
    def get_class_4_upper_rate(self) -> Decimal:
        class_4_nics_upper_rate = self._get_value_by_hmrc_constant(
            "NIC Class 4 upper rate"
        )

        self.l.debug(f"class_4_nics_upper_rate: {class_4_nics_upper_rate}")

        return class_4_nics_upper_rate

    @cache
    def get_dividends_basic_rate(self) -> Decimal:
        dividends_basic_rate = self._get_value_by_hmrc_constant("Dividends basic rate")

        self.l.debug(f"dividends_basic_rate: {dividends_basic_rate}")

        return dividends_basic_rate

    @cache
    def get_higher_tax_rate(self) -> Decimal:
        higher_tax_rate = self._get_value_by_hmrc_constant("Higher tax rate")

        self.l.debug(f"higher_tax_rate: {higher_tax_rate}")

        return higher_tax_rate

    @cache
    def get_savings_basic_rate(self) -> Decimal:
        savings_basic_rate = self._get_value_by_hmrc_constant("Savings basic rate")

        self.l.debug(f"savings_basic_rate: {savings_basic_rate}")

        return savings_basic_rate

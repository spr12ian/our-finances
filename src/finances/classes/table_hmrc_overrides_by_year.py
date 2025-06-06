
from sqlalchemy_helper import valid_sqlalchemy_name
from our_finances.classes.sqlite_table import SQLiteTable
from our_finances.util.financial_helpers import string_to_float
from functools import lru_cache


class HMRC_OverridesByYear(SQLiteTable):

    def __init__(self, person_code:str, tax_year:str) -> None:

        super().__init__("hmrc_overrides_by_year")
        self.person_code = person_code
        self.tax_year = tax_year
        self.tax_year_col = valid_sqlalchemy_name(tax_year)

    def _get_value_by_override(self, override) -> str:
        person_code = self.person_code
        tax_year = self.tax_year
        tax_year_col = self.tax_year_col
        query = (
            self.query_builder()
            .select(tax_year_col)
            .where(f'"person_code" = "{person_code}" AND "override" = "{override}"')
            .build()
        )
        result = self.sql.fetch_one_value(
            query
        )  # Could be formatted as a float, a ccy, etc.

        if result is None:
            raise ValueError(
                f"Could not find the override '{override}' for person {person_code}, tax year {tax_year}"
            )

        return result

    @lru_cache(maxsize=None)
    def deduct_trading_expenses(self) -> bool:
        deduct_trading_expenses = self._get_value_by_override(
            "Deduct trading expenses"
        )

        return deduct_trading_expenses == "Yes"

    @lru_cache(maxsize=None)
    def use_trading_allowance(self) -> bool:
        try:
            value = self._get_value_by_override("Use trading allowance")
        except ValueError as e:
            raise

        use_trading_allowance = value.lower() == "yes"

        return use_trading_allowance

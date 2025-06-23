from decimal import Decimal

from finances.classes.sqlite_table import SQLiteTable
from finances.util.financial_helpers import round_even


class Transactions(SQLiteTable):
    def __init__(self) -> None:
        super().__init__("transactions")

    def fetch_total_where(self, where_clause: str) -> Decimal:
        query = self.query_builder().total("nett").where(f"{where_clause}").build()
        total = self.sql.fetch_one_value_decimal(query)
        return round_even(Decimal(total))

    def fetch_total_by_tax_year_category(self, tax_year: str, category: str) -> Decimal:
        where_clause = f'"tax_year" = "{tax_year}" AND "category" = "{category}"'
        return self.fetch_total_where(where_clause)

    def fetch_total_by_tax_year_category_like(
        self, tax_year: str, category_like: str
    ) -> Decimal:
        where_clause = (
            f'"tax_year" = "{tax_year}" AND "category" LIKE "{category_like}%"'
        )
        return self.fetch_total_where(where_clause)

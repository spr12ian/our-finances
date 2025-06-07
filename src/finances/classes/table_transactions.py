from decimal import Decimal

import our_finances.util.financial_helpers as uf

from finances.classes.sqlite_table import SQLiteTable


class Transactions(SQLiteTable):
    def __init__(self) -> None:
        # self.l.set_level_debug()
        self.l.debug(__file__)

        super().__init__("transactions")

    def fetch_total_where(self, where_clause) -> Decimal:
        query = self.query_builder().total("nett").where(f"{where_clause}").build()
        self.l.debug(f"query: {query}")
        total = self.sql.fetch_one_value_decimal(query)
        self.l.debug(f"total: {total}")
        return uf.round_even(Decimal(total))

    def fetch_total_by_tax_year_category(self, tax_year, category) -> Decimal:
        where_clause = f'"tax_year" = "{tax_year}" AND "category" = "{category}"'
        return self.fetch_total_where(where_clause)

    def fetch_total_by_tax_year_category_like(self, tax_year, category_like) -> Decimal:
        where_clause = (
            f'"tax_year" = "{tax_year}" AND "category" LIKE "{category_like}%"'
        )
        return self.fetch_total_where(where_clause)

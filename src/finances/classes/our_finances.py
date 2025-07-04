from tables import *

from finances.classes.sqlite_helper import SQLiteHelper


class OurFinances:
    def __init__(self) -> None:
        self.sql = SQLiteHelper()

    def account_balances(self) -> Any:
        query = """
            SELECT key, balance 
            FROM account_balances
            WHERE balance NOT BETWEEN -1 AND 1
        """

        for row in self.sql.fetch_all(query):
            print(row)
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

    def people(self) -> Any:
        query = """
            SELECT * 
            FROM people
        """

        for row in self.sql.fetch_all(query):
            print(row)
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

    def transactions(self) -> Any:
        query = """
            SELECT category, SUM(nett) 
            FROM transactions
            WHERE key <> ''
            AND "tax_year" = '2023 to 2024'
            AND category LIKE 'HMRC%'
            GROUP BY category
        """

        for row in self.sql.fetch_all(query):
            print(row)
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

from our_finances.classes.sqlite_table import SQLiteTable


class BankAccounts(SQLiteTable):
    def __init__(self, key:str=None):
        super().__init__("bank_accounts")
        self.key = key

    def get_account_number(self):
        return self.get_value_by_key_column("account_number")

    def get_bank_name(self):
        return self.get_value_by_key_column("institution")

    def get_sort_code(self):
        return self.get_value_by_key_column("sort_code")

    def get_value_by_key_column(self, column_name):
        if self.key:
            query = (
                self.query_builder()
                .select(column_name)
                .where(f'"key" = "{self.key}"')
                .build()
            )
            result = self.sql.fetch_one_value(query)
        else:
            result = None

        return result

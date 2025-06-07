from finances.classes.date_time_helper import DateTimeHelper
from finances.classes.sqlite_table import SQLiteTable


class People(SQLiteTable):
    def __init__(self, code=None):
        super().__init__("people")
        self.code = code

    def fetch_by_code(self, code):
        query = self.query_builder().where(f"code = '{code}'").build()
        return self.sql.fetch_all(query)

    def get_address(self) -> Any:
        return self.get_value_by_code_column("address")

    def get_date_of_birth(self) -> Any:
        return self.get_value_by_code_column("date_of_birth")

    def get_email_address(self) -> Any:
        return self.get_value_by_code_column("email_address")

    def get_first_name(self) -> Any:
        return self.get_value_by_code_column("first_name")

    def get_last_name(self) -> Any:
        return self.get_value_by_code_column("last_name")

    def get_middle_name(self) -> Any:
        return self.get_value_by_code_column("middle_name")

    def get_name(self) -> Any:
        return self.get_value_by_code_column("person")

    def get_phone_number(self) -> Any:
        return self.get_value_by_code_column("phone_number")

    def get_uk_date_of_birth(self) -> Any:
        return DateTimeHelper().ISO_to_UK(self.get_date_of_birth())

    def get_value_by_code_column(self, column_name):
        if self.code:
            query = (
                self.query_builder()
                .select(column_name)
                .where(f'"code" = "{self.code}"')
                .build()
            )
            result = self.sql.fetch_one_value(query)
        else:
            result = None

        return result

from decimal import Decimal
from typing import Any
from finances.classes.date_time_helper import DateTimeHelper
from finances.classes.sqlite_table import SQLiteTable


class HMRC_PeopleDetails(SQLiteTable):
    def __init__(self, code=None):
        super().__init__("hmrc_people_details")
        self.code = code

    def _get_value_by_code_column(self, column_name):
        if self.code:
            query = (
                self.query_builder()
                .select(column_name)
                .where(f'"code" = "{self.code}"')
                .build()
            )
            result = str(self.sql.fetch_one_value(query))
        else:
            result = None

        return result

    def are_nics_needed_to_acheive_max_state_pension(self) -> bool:
        return (
            self._get_value_by_code_column("nics_needed_for_max_state_pension") == "Yes"
        )

    def fetch_by_code(self, code):
        query = self.query_builder().where(f"code = '{code}'").build()
        return self.sql.fetch_all(query)

    def get_marital_status(self) -> str:
        return self._get_value_by_code_column("marital_status")

    def get_marriage_date(self) -> str:
        return self._get_value_by_code_column("marriage_date")

    def get_national_insurance_number(self) -> str:
        return self._get_value_by_code_column("nino")

    def get_refunds_to(self) -> str:
        return self._get_value_by_code_column("refunds_to")

    def get_spouse_code(self) -> str:
        return self._get_value_by_code_column("spouse_code")

    def get_taxpayer_residency_status(self) -> str:
        return self._get_value_by_code_column("taxpayer_residency_status")

    def get_uk_marriage_date(self) -> Any:
        marriage_date = self.get_marriage_date()
        if marriage_date is None:
            return None
        else:
            return DateTimeHelper().ISO_to_UK(self.get_marriage_date())

    def get_unique_tax_reference(self) -> str:
        return self._get_value_by_code_column("utr")

    def get_utr_check_digit(self) -> str:
        utr_check_digit = self._get_value_by_code_column("utr_check_digit")
        if not utr_check_digit:
            utr_check_digit = ""
        return utr_check_digit

    def get_weekly_state_pension_forecast(self) -> Decimal:
        return Decimal(self._get_value_by_code_column("weekly_state_pension_forecast"))

    def is_married(self) -> bool:
        return self.get_marital_status() == "Married"

    def receives_child_benefit(self) -> bool:
        return self._get_value_by_code_column("receives_child_benefit") == "Yes"

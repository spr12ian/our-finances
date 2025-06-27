# standard imports
from __future__ import annotations

from decimal import Decimal
from functools import cache
from typing import Any

from finances.classes.table_bank_accounts import BankAccounts
from finances.classes.table_hmrc_people_details import HMRC_PeopleDetails

# local imports
from finances.classes.table_people import People


class HMRCPerson(People):
    def __init__(self, code: str) -> None:
        super().__init__(code)

        self.hmrc_person_details = HMRC_PeopleDetails(code)

    def are_nics_needed_to_achieve_max_state_pension(self) -> bool:
        return self.hmrc_person_details.are_nics_needed_to_achieve_max_state_pension()

    def get_bank_account_number(self) -> Any:
        refunds_to = self.hmrc_person_details.get_refunds_to()
        return BankAccounts(refunds_to).get_account_number()

    def get_bank_name(self) -> Any:
        refunds_to = self.hmrc_person_details.get_refunds_to()
        return BankAccounts(refunds_to).get_bank_name()

    def get_branch_sort_code(self) -> Any:
        refunds_to = self.hmrc_person_details.get_refunds_to()
        return BankAccounts(refunds_to).get_sort_code()

    def get_marital_status(self) -> Any:
        return self.hmrc_person_details.get_marital_status()

    def get_national_insurance_number(self) -> Any:
        return self.hmrc_person_details.get_national_insurance_number()

    def get_refunds_to(self) -> Any:
        return self.hmrc_person_details.get_refunds_to()

    def get_spouse_code(self) -> str | None:
        return self.hmrc_person_details.get_spouse_code()

    @cache
    def get_spouse_hmrc(self, tax_year: str) -> HMRC | None:
        from finances.classes.hmrc.core import HMRC

        return (
            HMRC(spouse_code, tax_year)
            if (spouse_code := self.get_spouse_code())
            else None
        )

    def get_taxpayer_residency_status(self) -> Any:
        return self.hmrc_person_details.get_taxpayer_residency_status()

    def get_uk_marriage_date(self) -> Any:
        marriage_date = self.hmrc_person_details.get_marriage_date()
        return marriage_date

    def get_unique_tax_reference(self) -> str | None:
        return self.hmrc_person_details.get_unique_tax_reference()

    def get_utr_check_digit(self) -> str:
        return self.hmrc_person_details.get_utr_check_digit()

    def get_weekly_state_pension_forecast(self) -> Decimal:
        weekly_state_pension_forecast = (
            self.hmrc_person_details.get_weekly_state_pension_forecast()
        )
        return Decimal(weekly_state_pension_forecast)

    def is_married(self) -> bool:
        return self.hmrc_person_details.is_married()

    def receives_child_benefit(self) -> bool:
        return self.hmrc_person_details.receives_child_benefit()

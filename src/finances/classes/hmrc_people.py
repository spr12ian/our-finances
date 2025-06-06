# standard imports
from decimal import Decimal
# local imports
from our_finances.classes.people import People
from tables import *

class HMRC_People(People):
    def __init__(self, code):
        super().__init__(code)

        self.hmrc_person_details = HMRC_PeopleDetails(code)

    def are_nics_needed_to_acheive_max_state_pension(self) -> bool:
        return self.hmrc_person_details.are_nics_needed_to_acheive_max_state_pension()

    def get_bank_account_number(self):
        refunds_to = self.hmrc_person_details.get_refunds_to()
        return BankAccounts(refunds_to).get_account_number()

    def get_bank_name(self):
        refunds_to = self.hmrc_person_details.get_refunds_to()
        return BankAccounts(refunds_to).get_bank_name()

    def get_branch_sort_code(self):
        refunds_to = self.hmrc_person_details.get_refunds_to()
        return BankAccounts(refunds_to).get_sort_code()

    def get_marital_status(self):
        return self.hmrc_person_details.get_marital_status()

    def get_national_insurance_number(self):
        return self.hmrc_person_details.get_national_insurance_number()

    def get_refunds_to(self):
        return self.hmrc_person_details.get_refunds_to()

    def get_spouse_code(self):
        return self.hmrc_person_details.get_spouse_code()

    def get_taxpayer_residency_status(self):
        return self.hmrc_person_details.get_taxpayer_residency_status()

    def get_uk_marriage_date(self):
        marriage_date = self.hmrc_person_details.get_marriage_date()
        return marriage_date

    def get_unique_tax_reference(self) -> str:
        return self.hmrc_person_details.get_unique_tax_reference()

    def get_utr_check_digit(self) -> str:
        return self.hmrc_person_details.get_utr_check_digit()

    def get_weekly_state_pension_forecast(self) -> Decimal:
        weekly_state_pension_forecast = (
            self.hmrc_person_details.get_weekly_state_pension_forecast()
        )
        self.l.debug(f"weekly_state_pension_forecast: {weekly_state_pension_forecast}")
        return Decimal(weekly_state_pension_forecast)

    def is_married(self) -> bool:
        return self.hmrc_person_details.is_married()

    def receives_child_benefit(self) -> bool:
        return self.hmrc_person_details.receives_child_benefit()

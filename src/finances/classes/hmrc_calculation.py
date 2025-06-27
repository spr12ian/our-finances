# standard imports
from datetime import datetime
from decimal import Decimal
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from finances.classes.hmrc.core import HMRC


class HMRC_Calculation:
    def __init__(self, hmrc: "HMRC") -> None:
        self.hmrc = hmrc
        self.output_list = [""]

    def add_extra_info(self) -> None:
        extra_info = ""
        start_date, end_date = self.get_current_tax_year_dates()
        # print(f"Tax Year Start Date: {start_date.strftime('%Y-%m-%d')}")
        # print(f"Tax Year End Date: {end_date.strftime('%Y-%m-%d')}")
        current_tax_year = f"Current Tax Year: {start_date.strftime('%Y')} to {end_date.strftime('%Y')}"
        hmrc = self.hmrc
        tax_year = hmrc.tax_year
        if tax_year == current_tax_year:
            weekly_state_pension = hmrc.get_weekly_state_pension()
            weekly_state_pension_gbp = self.gbp(weekly_state_pension)
            weekly_state_pension_forecast = hmrc.get_weekly_state_pension_forecast()
            weekly_state_pension_forecast_gbp = self.gbp(weekly_state_pension_forecast)

            extra_info += f"\nWeekly state pension: {weekly_state_pension_gbp}"
            extra_info += (
                f"\nWeekly state pension forecast: {weekly_state_pension_forecast_gbp}"
            )

        if extra_info:
            extra_info = "\n\n\nEXTRA INFO" + extra_info

        self.add_hmrc_part(extra_info)

    def add_hmrc_part(self, key: str, amount: Decimal | None = None) -> None:
        if amount is None:
            self.append(key)
        else:
            max_key_width = 65
            max_amount_width = 15
            amount_gbp = self.gbp(amount)
            line = f"{key.ljust(max_key_width)} {amount_gbp.rjust(max_amount_width)}"
            self.append(line)

    def add_part_basic_tax(self, unused_allowance) -> Decimal:
        hmrc = self.hmrc
        combined_taxable_profit = hmrc.get_combined_taxable_profit()
        p_taxable_amount = max(0, combined_taxable_profit - unused_allowance)
        if p_taxable_amount > 0:
            taxable_amount_gbp = hmrc.gbp(p_taxable_amount)
            basic_rate = hmrc.get_basic_tax_rate()
            label = f"Basic rate [{combined_taxable_profit} - {unused_allowance}] {taxable_amount_gbp} x{basic_rate}%"
            basic_tax = p_taxable_amount * basic_rate / 100
            self.add_hmrc_part(label, basic_tax)

            unused_allowance = max(0, unused_allowance - combined_taxable_profit)

        return unused_allowance

    def add_part_class_2_nics(self) -> None:
        hmrc = self.hmrc
        class_2_nics = hmrc.get_class_2_nics_due()
        self.add_hmrc_part(
            "Total Class 2 National Insurance contributions due", class_2_nics
        )

    def add_part_dividends(self) -> None:
        hmrc = self.hmrc
        dividends_income = hmrc.get_dividends_income()
        if dividends_income > 0:
            self.add_hmrc_part("Dividends from UK companies", dividends_income)

    def add_part_dividends_tax(self, unused_allowance) -> Decimal:
        hmrc = self.hmrc
        dividends_income = hmrc.get_dividends_income()
        d_taxable_amount = max(0, dividends_income - unused_allowance)
        if d_taxable_amount > 0:
            dividends_basic_rate = hmrc.get_dividends_basic_rate()
            dividends_allowance = hmrc.get_dividends_allowance()
            dividends_income = hmrc.get_dividends_income()
            taxable_amount = max(0, dividends_income - dividends_allowance)

            basic_tax = taxable_amount * dividends_basic_rate / 100
            taxable_amount_gbp = hmrc.gbp(taxable_amount)
            label = (
                f"Dividends basic rate {taxable_amount_gbp} x{dividends_basic_rate}%"
            )
            self.add_hmrc_part(label, basic_tax)

            unused_allowance = max(0, unused_allowance - dividends_income)

        return unused_allowance

    def add_part_income_tax(self) -> None:
        hmrc = self.hmrc
        income_tax = hmrc.get_income_tax()
        self.add_hmrc_part("Income tax due", income_tax)

    def add_part_marriage_allowance(self) -> None:
        hmrc = self.hmrc
        if hmrc.are_you_eligible_to_claim_marriage_allowance():
            marriage_allowance = hmrc.get_marriage_allowance_donor_amount()
            if marriage_allowance > 0:
                self.add_hmrc_part(
                    "lessMarriage Allowance transfer", marriage_allowance
                )
                hmrc_allowance = hmrc.get_hmrc_allowance()
                self.add_hmrc_part("Total", hmrc_allowance)
        elif hmrc.are_you_eligible_to_receive_marriage_allowance():
            marriage_allowance = hmrc.get_marriage_allowance_recipient_amount()
            if marriage_allowance > 0:
                self.add_hmrc_part(
                    "plusMarriage Allowance transfer", marriage_allowance
                )
                hmrc_allowance = hmrc.get_hmrc_allowance()
                self.add_hmrc_part("Total", hmrc_allowance)

    def add_part_minus(self) -> None:
        hmrc = self.hmrc
        self.add_hmrc_part("minus")

    def add_part_pay_pensions_profit(self, unused_allowance) -> None:
        hmrc = self.hmrc
        combined_taxable_profit = hmrc.get_combined_taxable_profit()
        p_taxable_amount = max(0, combined_taxable_profit - unused_allowance)
        if p_taxable_amount > 0:
            self.add_hmrc_part("Pay, pensions, profit etc.")

    def add_part_pension_payments(self) -> None:
        hmrc = self.hmrc
        pension_payments = hmrc.get_payments_to_pension_schemes__relief_at_source()
        revised_basic_rate_limit = self.get_revised_basic_rate_limit(pension_payments)
        if pension_payments > 0:
            pension_payments_gbp = hmrc.gbp(pension_payments)
            part = f"Pension payments of {pension_payments_gbp} increase basic rate limit to"
            self.add_hmrc_part(part, revised_basic_rate_limit)

    def add_part_personal_allowance(self) -> None:
        hmrc = self.hmrc
        personal_allowance = hmrc.get_personal_allowance()
        self.add_hmrc_part("Personal Allowance", personal_allowance)

    def add_part_property_profit(self) -> None:
        hmrc = self.hmrc
        property_profit = hmrc.get_property_profit()
        if property_profit > 0:
            self.add_hmrc_part("Profit from UK land and property", property_profit)

    def add_part_savings_basic_rate_tax(self, unused_allowance) -> Decimal:
        hmrc = self.hmrc
        savings_income = hmrc.get_savings_income()
        s_taxable_amount = max(0, savings_income - unused_allowance)
        if s_taxable_amount > 0:
            savings_basic_rate = hmrc.get_savings_basic_rate()
            savings_nil_band = hmrc.get_savings_nil_band()
            savings_income = hmrc.get_savings_income()
            taxable_amount = max(0, savings_income - savings_nil_band)

            basic_tax = taxable_amount * savings_basic_rate / 100
            taxable_amount_gbp = hmrc.gbp(taxable_amount)
            label = f"Basic rate {taxable_amount_gbp} x{savings_basic_rate}%"
            self.add_hmrc_part(label, basic_tax)

            unused_allowance = max(0, unused_allowance - savings_income)

        return unused_allowance

    def add_part_savings_interest(self, unused_allowance) -> None:
        hmrc = self.hmrc
        savings_income = hmrc.get_savings_income()
        s_taxable_amount = max(0, savings_income - unused_allowance)
        if s_taxable_amount > 0:
            self.add_hmrc_part(
                "Savings interest from banks or building societies, securities etc."
            )

    def add_part_savings_nil_rate_tax(self, unused_allowance) -> Decimal:
        hmrc = self.hmrc
        savings_income = hmrc.get_savings_income()
        s_taxable_amount = max(0, savings_income - unused_allowance)
        if s_taxable_amount > 0:
            savings_basic_rate = hmrc.get_savings_basic_rate()
            savings_nil_band = hmrc.get_savings_nil_band()
            savings_income = hmrc.get_savings_income()
            savings_nil_rate_amount = min(savings_income, savings_nil_band)
            taxable_amount = max(0, savings_income - savings_nil_band)
            basic_rate_integer = int(savings_basic_rate * 100)
            nil_rate_tax = Decimal(0)
            savings_nil_rate_amount_gbp = hmrc.gbp(savings_nil_rate_amount)
            label = f"Basic rate band at nil rate {savings_nil_rate_amount_gbp} x0%"
            self.add_hmrc_part(label, nil_rate_tax)

            unused_allowance = max(0, unused_allowance - savings_income)

        return unused_allowance

    def add_part_self_employment_profit(self) -> None:
        trading_profit = self.get_trading_profit()
        if trading_profit > 0:
            self.add_hmrc_part("Profit from self-employment", trading_profit)

    def add_part_total_and_nics(self) -> None:
        hmrc = self.hmrc
        income_tax = hmrc.get_income_tax()
        class_2_nics = hmrc.get_class_2_nics_due()
        total_for_this_year = income_tax + class_2_nics
        self.add_hmrc_part("Total tax + NICs due for this year", total_for_this_year)

    def add_part_total_income(self) -> Decimal:
        hmrc = self.hmrc
        hmrc_total_income = hmrc.get_hmrc_total_income()
        label = "Total income"
        if hmrc_total_income > 0:
            label += " on which tax is due"
        self.add_hmrc_part(label, hmrc_total_income)

        hmrc_allowance = hmrc.get_hmrc_allowance()

        unused_allowance = max(0, hmrc_allowance - hmrc_total_income)
        unused_allowance = hmrc_allowance

        return unused_allowance

    def add_part_total_income_received(self) -> None:
        hmrc = self.hmrc
        total_income_received = hmrc.get_hmrc_total_income_received()
        if total_income_received > 0:
            self.add_hmrc_part("Total income received", total_income_received)

    def add_part_uk_interest(self) -> None:
        hmrc = self.hmrc
        savings_income = hmrc.get_savings_income()
        if savings_income > 0:
            self.add_hmrc_part(
                "Interest from UK banks, building societies and securities etc",
                savings_income,
            )

    def append(self, string) -> None:
        self.output_list.append(string)

    def gbp(self, amount) -> str:
        return self.hmrc.gbp(amount)

    def get_basic_rate_limit(self) -> Decimal:
        hmrc = self.hmrc
        basic_rate_threshold = hmrc.get_basic_rate_threshold()
        personal_allowance = hmrc.get_personal_allowance()
        basic_rate_limit = basic_rate_threshold - personal_allowance
        return basic_rate_limit

    def get_current_tax_year_dates(self) -> Any:
        today = datetime.today()
        current_year = today.year
        tax_year_start = datetime(current_year, 4, 6)
        tax_year_end = datetime(current_year + 1, 4, 5)

        if today < tax_year_start:
            tax_year_start = datetime(current_year - 1, 4, 6)
            tax_year_end = datetime(current_year, 4, 5)

        return tax_year_start, tax_year_end

    def get_output(self) -> str:
        self.add_part_self_employment_profit()
        self.add_part_property_profit()
        self.add_part_uk_interest()
        self.add_part_dividends()
        self.add_part_total_income_received()
        self.add_part_minus()
        self.add_part_personal_allowance()
        self.add_part_marriage_allowance()
        unused_allowance = self.add_part_total_income()
        self.add_part_pay_pensions_profit(unused_allowance)
        self.add_part_pension_payments()
        unused_allowance = self.add_part_basic_tax(unused_allowance)
        self.add_part_savings_interest(unused_allowance)
        unused_allowance = self.add_part_savings_nil_rate_tax(unused_allowance)
        unused_allowance = self.add_part_savings_basic_rate_tax(unused_allowance)
        unused_allowance = self.add_part_dividends_tax(unused_allowance)
        self.add_part_income_tax()
        self.add_part_class_2_nics()
        self.add_part_total_and_nics()
        self.add_extra_info()

        return "\n".join(self.output_list)

    def get_revised_basic_rate_limit(self, pension_payments) -> Decimal:
        hmrc = self.hmrc
        basic_rate_limit = self.get_basic_rate_limit()
        revised_basic_rate_limit = basic_rate_limit + pension_payments
        return revised_basic_rate_limit

    def get_trading_profit(self) -> Decimal:
        return self.hmrc.get_trading_profit()

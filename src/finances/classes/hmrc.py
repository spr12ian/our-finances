# standard imports
from functools import lru_cache
from decimal import Decimal
# local imports
from our_finances.classes.sql_helper import SQL_Helper
from our_finances.classes.sqlalchemy_helper import valid_sqlalchemy_name
from our_finances.classes.hmrc_calculation import HMRC_Calculation
from our_finances.classes.hmrc_people import HMRC_People
from our_finances.util import boolean_helpers, financial_helpers
from tables import *
from our_finances.classes.hmrc_output import HMRC_Output


class HMRC:

    def __init__(self, person_code: str, tax_year: str):
        self.l = LogHelper("HMRC")
        self.l.set_level_debug()
        self.l.debug(__file__)
        self.l.debug(f"person_code: {person_code}")
        self.l.debug(f"tax_year: {tax_year}")

        self.person_code = person_code
        self.tax_year = tax_year
        self.tax_year_col = valid_sqlalchemy_name(tax_year)

        self.categories = Categories()
        self.constants = HMRC_ConstantsByYear(tax_year)
        self.overrides = HMRC_OverridesByYear(person_code, tax_year)
        self.person = HMRC_People(person_code)
        if self.is_married():
            spouse_code = self.person.get_spouse_code()
            self.spouse = HMRC_People(spouse_code)
        self.sql = SQL_Helper().select_sql_helper("SQLite")
        self.transactions = Transactions()

    def _get_breakdown(self, category_like):
        tax_year = self.tax_year
        query = (
            self.transactions.query_builder()
            .select("date", "key", "description", "note", "nett", "category")
            .where(f'"tax_year"="{tax_year}" AND "category" LIKE "{category_like}%"')
            .order("date")
            .build()
        )
        self.l.debug(query)
        rows = self.sql.fetch_all(query)
        if not rows:
            return ""
        max_description_width = 40
        max_category_width = max_description_width
        breakdown = ["Date | Account | Description | Note | Nett (£) | Category"]
        for row in rows:
            self.l.debug(f"row: {row}")
            nett_decimal = Decimal(row[4])
            self.l.debug(f"nett_decimal: {nett_decimal:>10.2f}")
            breakdown.append(
                f"{row[0]} | {row[1]} | {row[2][:max_description_width]} | {row[3]} | {nett_decimal:>10.2f} | {row[5][:max_category_width]}"
            )
        return self.format_breakdown(breakdown)

    def are_any_of_these_figures_provisional(self):
        return False

    def are_computations_provided(self):
        return False

    def are_nics_needed_to_acheive_max_state_pension(self) -> bool:
        self.l.debug("are_nics_needed_to_acheive_max_state_pension")
        are_nics_needed_to_acheive_max_state_pension = (
            self.person.are_nics_needed_to_acheive_max_state_pension()
        )
        if are_nics_needed_to_acheive_max_state_pension:
            self.l.debug("nics are needed to acheive max state pension")
        else:
            self.l.debug("nics are NOT needed to acheive max state pension")

        return are_nics_needed_to_acheive_max_state_pension

    def are_supplementary_pages_enclodsed(self):
        return self.gbpb(0)

    def are_supplementary_pages_enclosed(self):
        return False

    def are_there_digest_transactions(self, digest_type) -> bool:
        self.l.debug("are_there_digest_transactions")
        digest_category_like = self.get_digest_type_categories()[digest_type]
        self.l.debug(f"digest_category_like: {digest_category_like}")
        person_code = self.person.code
        tax_year = self.tax_year
        query = (
            self.transactions.query_builder()
            .select_raw("COUNT(DISTINCT category)")
            .where(
                f'"tax_year"="{tax_year}"'
                + f' AND "category" LIKE "HMRC {person_code}{digest_category_like}%"'
            )
            .build()
        )
        self.l.debug(f"query: {query}")
        how_many = self.sql.fetch_one_value(query)
        self.l.debug(f"how_many: {how_many}")
        return how_many > 0

    def are_there_dividends_transactions(self) -> bool:
        income = self.get_dividends_income()
        self.l.debug(f"income: {income}")
        if income > 0:
            return True
        return False

    def are_there_more_pages(self):
        return False

    def are_there_property_transactions(self) -> bool:
        income = self.get_property_income()
        self.l.debug(f"income: {income}")
        if income > 0:
            return True
        expenses = self.get_property_expenses_actual()
        self.l.debug(f"expenses: {expenses}")
        if expenses > 0:
            return True
        return False

    def are_there_savings_transactions(self) -> bool:
        income = self.get_savings_income()
        self.l.debug(f"income: {income}")
        if income > 0:
            return True
        return False

    def are_there_trading_transactions(self) -> bool:
        income = self.get_trading_income()
        self.l.debug(f"income: {income}")
        if income > 0:
            return True
        expenses = self.get_trading_expenses_actual()
        self.l.debug(f"expenses: {expenses}")
        if expenses > 0:
            return True
        return False

    def are_you_a_diver(self):
        return False

    def are_you_a_farmer(self):
        return False

    def are_you_a_foster_carer(self):
        return False

    def are_you_a_trustee__executor_or_administrator(self):
        return False

    def are_you_acting_in_capacity_on_behalf_of_someone_else(self):
        return False

    def are_you_affected_by_basis_period_reform(self):
        return False

    def are_you_claiming__overlap_relief_(self):
        return False

    def are_you_claiming_back_cis_tax_already_paid(self):
        return False

    def are_you_claiming_marriage_allowance(self):
        if not self.is_married():
            return False
        total_income = self.get_hmrc_total_income_received()
        spouse_total_income = self.get_spouse_total_income_received()
        if total_income > spouse_total_income:
            return False
        personal_allowance = self.get_personal_allowance()
        total_income_excluding_tax_free_savings = (
            self.get_total_income_excluding_tax_free_savings()
        )
        if total_income_excluding_tax_free_savings > personal_allowance:
            return False
        return True

    def are_you_claiming_married_couple_s_allowance(self):
        return False

    def are_you_claiming_other_tax_reliefs(self):
        return False

    def are_you_claiming_relief_for_a_loss(self):
        trading_income = self.get_trading_income()
        trading_allowance = self.get_trading_allowance_actual()
        loss = self.get_trading_loss()
        return trading_income <= trading_allowance and loss > 0

    def are_you_claiming_rent_a_room_relief(self):
        return False

    def are_you_eligible_to_claim_marriage_allowance(self):
        if not self.is_married():
            return False
        total_income = self.get_hmrc_total_income_received()
        spouse_total_income = self.get_spouse_total_income_received()
        personal_allowance = self.get_personal_allowance()
        higher_rate_threshold = self.get_higher_rate_threshold()
        return (
            total_income < personal_allowance
            and personal_allowance < spouse_total_income
            and spouse_total_income < higher_rate_threshold
        )

    def are_you_eligible_to_receive_marriage_allowance(self):
        if not self.is_married():
            return False
        total_income = self.get_hmrc_total_income_received()
        spouse_total_income = self.get_spouse_total_income_received()
        personal_allowance = self.get_personal_allowance()
        higher_rate_threshold = self.get_higher_rate_threshold()
        return (
            spouse_total_income < personal_allowance
            and personal_allowance < total_income
            and total_income < higher_rate_threshold
        )

    def are_you_exempt_from_paying_class_4_nics(self):
        return not self.did_none_of_these_apply__class_4_nics_()

    def are_you_liable_to_pension_savings_tax_charges(self):
        return False

    def are_you_registered_blind(self):
        return False

    def calculate_dividends_tax(self, amount, available_allowance=0):
        self.l.debug("calculate_dividends_tax")
        self.l.debug(f"amount: {amount}")
        self.l.debug(f"available_allowance: {available_allowance}")
        if amount <= available_allowance:
            tax = 0
            available_allowance -= amount
        else:
            amount -= available_allowance
            available_allowance = 0
            dividends_allowance = self.get_dividends_allowance()
            if amount <= dividends_allowance:
                tax = 0
            else:
                dividends_basic_rate = self.get_dividends_basic_rate()
                tax = (amount - dividends_allowance) * dividends_basic_rate
        self.l.debug(f"tax: {tax}")
        return (round(tax, 2), available_allowance)

    def calculate_savings_tax(self, amount, available_allowance=0):
        self.l.debug("calculate_savings_tax")
        self.l.debug(f"amount: {amount}")
        self.l.debug(f"available_allowance: {available_allowance}")
        if amount <= available_allowance:
            tax = 0
            available_allowance -= amount
        else:
            amount -= available_allowance
            available_allowance = 0
            savings_nil_band = self.get_savings_nil_band()
            if amount <= savings_nil_band:
                tax = 0
            else:
                savings_basic_rate = self.get_savings_basic_rate() / 100
                tax = (amount - savings_nil_band) * savings_basic_rate
        self.l.debug(f"tax: {tax}")
        return (round(tax, 2), available_allowance)

    def calculate_tax(self, amount, available_allowance):
        self.l.debug("calculate_tax")
        self.l.debug(f"amount: {amount}")
        self.l.debug(f"available_allowance: {available_allowance}")
        if amount <= available_allowance:
            tax = 0
            available_allowance -= amount
        else:
            amount -= available_allowance
            available_allowance = 0
            basic_rate_threshold = self.get_revised_basic_rate_threshold()
            basic_rate_limit = self.get_basic_rate_limit()
            higher_rate_threshold = self.get_higher_rate_threshold()
            additional_tax_rate = self.get_additional_tax_rate() / 100
            basic_tax_rate = self.get_basic_tax_rate() / 100
            higher_tax_rate = self.get_higher_tax_rate() / 100
            if amount <= basic_rate_limit:
                tax = amount * basic_tax_rate
            else:
                higher_rate_limit = higher_rate_threshold - basic_rate_threshold
                if amount <= higher_rate_limit:
                    tax = (
                        amount * basic_tax_rate
                        + (amount - basic_rate_limit) * higher_tax_rate
                    )
                else:
                    tax = (
                        amount * basic_tax_rate
                        + (higher_rate_limit - basic_rate_limit) * higher_tax_rate
                        + (amount - higher_rate_limit) * additional_tax_rate
                    )
        self.l.debug(f"tax: {tax}")
        return (round(tax, 2), available_allowance)

    def call_method(self, method_name):
        self.l.debug(f"Calling method: {method_name}")
        if not self.does_method_exist(method_name):
            self.l.error(f"\tdef {method_name}(self): return self.gbpb(0)")
            return f"Method not found: {method_name} - check log file"
        method = getattr(self, method_name)
        return method()

    def ceased_renting__consider_cgt(self):
        return self.gbpb(0)

    def deduct_trading_expenses(self):
        self.l.debug("deduct_trading_expenses")
        try:
            return self.deduct_trading_expenses_override()
        except ValueError as v:
            trading_allowance = self.get_trading_allowance_actual()
            trading_expenses = self.get_trading_expenses_actual()
            return trading_allowance < trading_expenses

    def deduct_trading_expenses_override(self):
        self.l.debug("deduct_trading_expenses_override")
        try:
            return self.overrides.deduct_trading_expenses()
        except ValueError as v:
            self.l.info(v)
            raise

    def did_business_details_change(self):
        return False

    def did_none_of_these_apply__business_1_page_1__(self):
        self.l.debug("did_none_of_these_apply__business_1_page_1__")
        self.l.debug(f"person_code: {self.person_code}")
        self.l.debug(f"tax_year: {self.tax_year}")
        conditions = [
            self.are_you_a_foster_carer(),
            self.do_you_wish_to_make_an_adjustment_to_your_profits(),
            self.are_you_a_farmer(),
            self.were_any_results_already_declared_on_a_previous_return(),
            self.is_the_basis_period_different_to_the_accounting_period(),
            self.is_your_business_carried_on_abroad(),
            self.are_you_claiming__overlap_relief_(),
            self.should_you_pay_voluntary_class_2_nics__turnover___ta(),
            self.are_you_claiming_back_cis_tax_already_paid(),
            self.are_you_claiming_relief_for_a_loss(),
        ]
        return boolean_helpers.all_conditions_are_false(conditions)

    def did_none_of_these_apply__class_4_nics_(self):
        conditions = [
            self.were_you_over_state_pension_age_at_tax_year_start(),
            self.were_you_under_16_at_tax_year_start(),
            self.were_you_not_resident_in_uk_during_the_tax_year(),
            self.are_you_a_trustee__executor_or_administrator(),
            self.are_you_a_diver(),
        ]
        return boolean_helpers.all_conditions_are_false(conditions)

    def did_property_rental_income_cease(self):
        return False

    def did_you_get_any_foreign_income(self):
        return False

    def did_you_get_any_income_tax_refund(self):
        return False

    def did_you_get_child_benefit(self):
        return self.receives_child_benefit()

    def did_you_get_dividends_income(self):
        person_code = self.person_code
        tax_year = self.tax_year
        category_like = f"HMRC {person_code} DIV income: "
        total = self.transactions.fetch_total_by_tax_year_category_like(
            tax_year, category_like
        )
        return total > 0

    def did_you_get_eea_furnished_holiday_lettings_income(self):
        return False

    def did_you_get_income_from_property_let_jointly(self):
        how_many_properties_do_you_rent_out = (
            self.get_how_many_properties_do_you_rent_out()
        )
        if not how_many_properties_do_you_rent_out:
            return False
        rented_property_postcode = self.get_rented_property_postcode()
        hmrc_property = HMRC_Property(rented_property_postcode)
        is_let_jointly = hmrc_property.is_let_jointly()
        self.l.debug(f"is_let_jointly: {is_let_jointly}")
        return is_let_jointly

    def did_you_get_other_taxable_income(self):
        return False

    def did_you_get_pensions__annuities__or_state_benefits(self):
        total = self.get_private_pensions_income() + self.get_taxable_benefits_income()
        return total > 0

    def did_you_get_student_loans_company_notification(self):
        return False

    def did_you_get_trust_income(self):
        return False

    def did_you_get_uk_furnished_holiday_lettings_income(self):
        return False

    def did_you_get_uk_interest(self):
        taxed_uk_interest = self.get_taxed_uk_interest()
        untaxed_uk_interest = self.get_untaxed_uk_interest()
        total_interest = taxed_uk_interest + untaxed_uk_interest
        return total_interest > 0

    def did_you_give_to_charity(self):
        return False

    def did_you_have_a_tax_advisor(self):
        return False

    def did_you_make_a_loss(self):
        return False

    def did_you_make_pension_contributions(self):
        pension_contributions = self.get_pension_contributions()
        return pension_contributions > 0

    def did_you_put_a_nominee_s_name_in_box_5(self):
        return False

    def did_you_use_cash_basis(self):
        return True

    def did_you_use_tax_avoidance_schemes(self):
        return False

    def did_you_use_traditional_accounting(self):
        return False

    def disable_debug(self):
        self.l.disable()

    def do_you_need__additional_information__pages_tr(self):
        return ""

    def do_you_need_to_complete_the_capital_gains_section(self):
        return False

    def do_you_want_paye_for_small_amount_payments(self):
        return False

    def do_you_want_paye_for_tax_on_savings(self):
        return False

    def do_you_want_refunds_by_cheque(self):
        return False

    def do_you_want_spouse_s_surplus_allowance(self):
        return "What is this"

    def do_you_want_to_add_an_attachment_to_the_return(self):
        return False

    def do_you_want_to_pay_class_2_nics_voluntarily(self):
        taxable_profits = self.get_total_taxable_profits_from_this_business()
        small_profits_threshold = self.get_small_profits_threshold()
        return taxable_profits < small_profits_threshold

    def do_you_want_to_reduce_next_year_payments_on_account(self):
        return False

    def do_you_wish_to_make_an_adjustment_to_your_profits(self) -> bool:
        return False

    def do_you_wish_to_voluntarily_pay_class_2_nics(self) -> bool:
        self.l.debug("do_you_wish_to_voluntarily_pay_class_2_nics")
        trading_income = self.get_trading_income()
        personal_allowance = self.get_personal_allowance()
        if trading_income > personal_allowance:
            return False
        small_profits_threshold = self.get_small_profits_threshold()
        if trading_income > small_profits_threshold:
            return False
        return self.are_nics_needed_to_acheive_max_state_pension()

    def does_method_exist(self, method_name):
        self.l.debug(f"Does method exist: '{method_name}'?")
        method = getattr(self, method_name, None)
        return method is not None

    def does_this_return_contain_provisional_figures(self):
        return False

    def enable_debug(self):
        self.l.enable()

    def format_breakdown(self, breakdown) -> str:
        fields = [line.split("|") for line in breakdown]
        max_widths = [
            max((len(field.strip()) for field in col)) for col in zip(*fields)
        ]
        formatted_lines = [
            " | ".join(
                (
                    (
                        field.strip().ljust(width)
                        if index != 4
                        else field.strip().rjust(width)
                    )
                    for (index, (field, width)) in enumerate(zip(line, max_widths))
                )
            )
            for line in fields
        ]
        return "\n" + "\n".join(formatted_lines) + "\n"

    def gbp(self, amount: Decimal, field_width: int = 0) -> str:
        return financial_helpers.format_as_gbp(amount, field_width)

    def gbpa(self, amount: Decimal, field_width: int = 10) -> str:
        return self.gbp(amount, field_width)

    def gbpb(self, amount: Decimal) -> str:
        if abs(amount) < 0.01:
            return ""
        return self.gbpa(amount)

    def get_additional_information(self):
        return "Maybe: Married couples allowance section"

    def get_additional_rate_threshold(self) -> Decimal:
        return self.constants.get_additional_rate_threshold()

    def get_additional_tax_rate(self):
        self.l.debug("get_additional_tax_rate")
        additional_tax_rate = self.constants.get_additional_tax_rate()
        self.l.debug(f"additional_tax_rate: {additional_tax_rate}")
        return additional_tax_rate

    def get_adjusted_loss_for_the_year(self):
        return self.gbpb(0)

    def get_adjusted_loss_for_the_year_gbp(self):
        return self.gbpb(0)

    def get_adjusted_profit_for_the_year(self):
        income = self.get_property_income()
        expenses = self.get_property_expenses_actual()
        adjusted_profit_for_the_year = income - expenses
        return adjusted_profit_for_the_year

    def get_adjusted_profit_for_the_year_gbp(self):
        return self.gbpb(self.get_adjusted_profit_for_the_year())

    def get_adjusted_profit_or_loss_for_the_year_gbp(self):
        return self.gbpb(0)

    def get_adjusted_property_profit_or_loss_for_the_year(self):
        return self.get_property_taxable_profit_for_the_year()

    def get_adjusted_property_profit_or_loss_for_the_year_gbp(self):
        return self.gbpb(self.get_adjusted_property_profit_or_loss_for_the_year())

    def get_adjustments_gbp(self):
        return self.gbpb(0)

    def get_all_other_capital_allowances(self):
        return self.gbpb(0)

    def get_all_other_capital_allowances_gbp(self):
        return self.gbpb(0)

    def get_amount_in_box_3_not_subject_to_income_tax_relief_limit(self):
        return self.gbpb(0)

    def get_amount_of_payroll_giving(self):
        return self.gbpb(0)

    def get_amount_of_underpaid_tax_for_earlier_years__paye__gbp(self):
        return self.gbpb(0)

    def get_amount_saved_to_pension___available_lifetime_allowance(self):
        return self.gbpb(0)

    def get_amount_subject_to_overseas_transfer_charge(self):
        return self.gbpb(0)

    def get_annual_allowance_tax_paid(self):
        return self.gbpb(0)

    def get_annual_investment_allowance_gbp(self):
        return ""

    def get_annual_payments_made(self):
        return self.gbpb(0)

    def get_answers(self) -> list:
        questions = self.get_questions()
        answers = []
        for question, section, header, box, method_name, information in questions:
            answer = self.call_method(method_name)
            answers.append([question, section, header, box, answer, information])
        return answers

    def get_any_employer_deducted_post_grad_loan(self):
        return self.gbpb(0)

    def get_any_employer_deducted_student_loan(self):
        return self.gbpb(0)

    def get_any_next_year_repayment_you_are_claiming_now_gbp(self):
        return self.gbpb(0)

    def get_any_other_information(self):
        return False

    def get_any_other_information_about_your_uk_property_income(self):
        return self.gbpb(0)

    def get_any_repayments_claimed_for_next_year(self):
        return self.gbpb(0)

    def get_any_tax_taken_off_box_17(self):
        return 0

    def get_bank_account_holder(self):
        return self.person.get_name()

    def get_bank_account_number(self):
        return self.person.get_bank_account_number()

    def get_bank_name(self):
        return self.person.get_bank_name()

    def get_basic_rate_limit(self):
        self.l.debug("get_basic_rate_limit")
        basic_rate_threshold = self.get_revised_basic_rate_threshold()
        self.l.debug(f"basic_rate_threshold: {basic_rate_threshold}")
        tax_free_allowance = self.get_hmrc_allowance()
        self.l.debug(f"tax_free_allowance: {tax_free_allowance}")
        basic_rate_limit = basic_rate_threshold - tax_free_allowance
        self.l.debug(f"basic_rate_limit: {basic_rate_limit}")
        return basic_rate_limit

    def get_basic_rate_threshold(self):
        return self.constants.get_basic_rate_threshold()

    def get_basic_tax_rate(self) -> Decimal:
        self.l.debug("get_basic_tax_rate")
        basic_tax_rate = self.constants.get_basic_tax_rate()
        self.l.debug(f"basic_tax_rate: {basic_tax_rate}")
        return basic_tax_rate

    def get_benefit_from_pre_owned_assets(self):
        return 0

    def get_blind_person_s_surplus_allowance_you_can_have(self):
        return self.gbpb(0)

    def get_bonus_issues(self):
        return self.gbpb(0)

    def get_bottom_line(self):
        return self.get_business_income() - self.get_trading_expenses()

    def get_bottom_line_gbp(self):
        return self.gbpb(self.bottom_line())

    def get_box_11_is_not_in_use(self):
        return self.gbpb(0)

    def get_box_17_is_not_in_use(self):
        return self.gbpb(0)

    def get_box_2_is_not_is_use(self):
        return self.gbpb(0)

    def get_branch_sort_code(self):
        return self.person.get_branch_sort_code()

    def get_building_society_reference_number(self):
        return self.gbpb(0)

    def get_business_description(self):
        if self.get_how_many_businesses() > 0:
            business_name = self.get_business_name()
            hmrc_business = HMRC_Businesses(business_name)
            business_description = hmrc_business.get_business_description()
            return business_description
        else:
            return ""

    def get_business_end_date(self):
        return ""

    def get_business_end_date__in_this_tax_year_(self):
        return self.gbpb(0)

    def get_business_income(self):
        return (
            self.get_trading_income()
            + self.get_other_business_income_not_included_as_trading_income()
        )

    def get_business_income_gbp(self):
        return self.gbpb(self.get_business_income())

    def get_business_name(self):
        if self.get_how_many_businesses() > 0:
            hmrc_businesses = self.get_hmrc_businesses()
            return hmrc_businesses[0].get_business_name()
        else:
            return self.gbpb(0)

    def get_business_postcode(self):
        if self.get_how_many_businesses() > 0:
            business_name = self.get_business_name()
            hmrc_business = HMRC_Businesses(business_name)
            business_postcode = hmrc_business.get_business_postcode()
            return business_postcode
        else:
            return ""

    def get_business_start_date(self):
        return ""

    def get_business_start_date__in_this_tax_year_(self):
        return self.gbpb(0)

    def get_capital_allowances_gbp(self):
        return self.gbpb(0)

    def get_capital_gains_tax_due(self):
        return self.gbpb(0)

    def get_class_2_annual_amount(self):
        return self.constants.get_class_2_annual_amount()

    def get_class_2_nics_due(self):
        self.l.debug("get_class_2_nics_due")
        class_2_annual_amount = self.get_class_2_annual_amount()

        # If trading profits exceed the personal allowance
        # then class 2 nics payments are required.
        personal_allowance = self.get_personal_allowance()
        trading_profit = self.get_trading_profit()
        if trading_profit >= personal_allowance:
            return class_2_annual_amount

        # If trading profits between small profits threshold and personal allowance
        # then class 2 nics are deemed to have been paid.
        # This rule may be year dependednt.
        small_profits_threshold = self.get_small_profits_threshold()
        if trading_profit >= small_profits_threshold:
            return 0

        # If trading profits less than small profits threshold
        # then class 2 nics are voluntary.
        # Pay voluntarily if neccesary to acheive max state pension.
        if self.are_nics_needed_to_acheive_max_state_pension():
            return class_2_annual_amount

        return 0

    def get_class_2_nics_due_gbp(self):
        return self.gbpa(self.get_class_2_nics_due())

    def get_class_2_weekly_rate(self):
        return self.constants.get_class_2_weekly_rate()

    def get_class_4_lower_profits_limit(self) -> Decimal:
        return self.constants.get_class_4_lower_profits_limit()

    def get_class_4_lower_rate(self) -> Decimal:
        return self.constants.get_class_4_lower_rate()

    def get_class_4_nics_due(self) -> Decimal:
        class_4_nics_lower_rate = self.get_class_4_lower_rate()
        class_4_nics_upper_rate = self.get_class_4_upper_rate()
        lower_profits_limit = self.get_class_4_lower_profits_limit()
        upper_profits_limit = self.get_class_4_upper_profits_limit()
        trading_profit = self.get_trading_profit()
        self.l.debug(f"trading_profit: {trading_profit}")
        if trading_profit <= lower_profits_limit:
            class_4_nics_due = 0.0
        elif trading_profit <= upper_profits_limit:
            class_4_nics_due = (
                trading_profit - lower_profits_limit
            ) * class_4_nics_lower_rate
        else:
            lower_band_nic = (
                upper_profits_limit - lower_profits_limit
            ) * class_4_nics_lower_rate
            upper_band_nic = (
                trading_profit - upper_profits_limit
            ) * class_4_nics_upper_rate
            class_4_nics_due = lower_band_nic + upper_band_nic
        self.l.debug(f"class_4_nics_due: {class_4_nics_due}")
        return Decimal(class_4_nics_due)

    def get_class_4_nics_due_gbp(self):
        return self.gbpa(self.get_class_4_nics_due())

    def get_class_4_upper_profits_limit(self):
        return self.constants.get_class_4_lower_profits_limit()

    def get_class_4_upper_rate(self):
        return self.constants.get_class_4_upper_rate()

    def get_combined_tax_digest(self):
        self.l.debug("get_combined_tax_digest")
        combined_taxable_profit = self.get_combined_taxable_profit()
        combined_taxable_profit_gbp = self.gbp(combined_taxable_profit)
        personal_allowance = self.get_personal_allowance()
        personal_allowance_gbp = self.gbp(personal_allowance)
        taxable_amount = max(0, combined_taxable_profit - personal_allowance)
        taxable_amount_gbp = self.gbp(taxable_amount)
        (tax, unused_allowance) = self.calculate_tax(
            combined_taxable_profit, personal_allowance
        )
        self.unused_allowance = unused_allowance
        tax_gbp = self.gbp(tax)
        class_2_nics_due_gbp = self.get_class_2_nics_due_gbp().strip()
        class_4_nics_due_gbp = self.get_class_4_nics_due_gbp().strip()
        parts = [f"Combined taxable profit: {combined_taxable_profit_gbp}"]
        parts.append(f"personal allowance: {personal_allowance_gbp}")
        parts.append(f"taxable amount: {taxable_amount_gbp}")
        parts.append(f"tax: {tax_gbp}")
        parts.append(f"class 2 nics: {class_2_nics_due_gbp}")
        parts.append(f"class 4 nics: {class_4_nics_due_gbp}")
        return "\n" + " | ".join(parts)

    def get_combined_taxable_profit(self) -> Decimal:
        trading_profit = self.get_trading_profit()
        property_profit = self.get_property_profit()
        combined_taxable_profit = trading_profit + property_profit
        return combined_taxable_profit

    def get_combined_taxable_profit_gbp(self) -> str:
        return self.gbpb(self.get_combined_taxable_profit())

    def get_community_investment_tax_relief(self):
        return self.gbpb(0)

    def get_compensation_and_lump_sums_up_to__30_000_exemption(self):
        return self.gbpb(0)

    def get_construction_industry_deductions_gbp(self):
        return False

    def get_cost_to_replace_residential_domestic_items(self) -> Decimal:
        self.l.debug("get_cost_to_replace_residential_domestic_items")
        category_like = "UKP expense: cost of replacing domestic items"
        cost_to_replace_residential_domestic_items = (
            self.get_total_transactions_by_category_like(category_like)
        )
        self.l.debug(
            f"cost_to_replace_residential_domestic_items: {cost_to_replace_residential_domestic_items}"
        )
        return self.round_up(cost_to_replace_residential_domestic_items)

    def get_cost_to_replace_residential_domestic_items_gbp(self) -> str:
        self.l.debug("get_cost_to_replace_residential_domestic_items_gbp")
        return self.gbpb(self.get_cost_to_replace_residential_domestic_items())

    def get_costs_of_services_provided__including_wages(self):
        return 0

    def get_costs_of_services_provided__including_wages_gbp(self):
        return self.gbpb(self.get_costs_of_services_provided__including_wages())

    def get_date_cb_stopped(self):
        return self.gbpb(0)

    def get_date_the_books_are_made_up_to(self):
        end_year = self.tax_year[-4:]
        return f"05/04/{end_year}"

    def get_declaration_date(self):
        return self.gbpb(0)

    def get_declaration_signature(self):
        return self.gbpb(0)

    def get_decrease_in_tax_due_to_adjustments_to_an_earlier_year(self):
        return self.gbpb(0)

    def get_decrease_in_tax_due_to_earlier_years_adjustments(self):
        return 0

    def get_decrease_in_tax_due_to_earlier_years_adjustments_gbp(self):
        return self.gbpb(self.get_decrease_in_tax_due_to_earlier_years_adjustments())

    def get_deficiency_relief(self):
        return self.gbpb(0)

    def get_description_of_income_in_boxes_17_and_20(self):
        return ""

    def get_digest(self, d):
        digest = "\n"
        for key, value in d.items():
            digest += f"{key}: {self.gbp(value)} "
        digest += "\n"
        return digest

    def get_digest_by_type(self, digest_type):
        self.l.debug("get_digest_by_type")
        self.l.debug(f"digest_type: {digest_type}")
        if not self.are_there_digest_transactions(digest_type):
            return ""
        parts = []
        income_gbp = self.get_digest_income_gbp(digest_type)

        if self.use_trading_allowance():
            parts.append("use_trading_allowance: True")
        else:
            parts.append("use_trading_allowance: False")
        deductible_gbp = self.get_digest_deductible_gbp(digest_type)
        deductible_label = self.get_digest_deductible_label(digest_type)
        taxable_gbp = self.get_digest_taxible_gbp(digest_type)
        parts.append(f"{digest_type.upper()} income: {income_gbp}")
        parts.append(f"{digest_type} {deductible_label}: {deductible_gbp}")
        parts.append(f"taxable {digest_type}: {taxable_gbp}")
        return "\n" + " | ".join(parts)

    def get_digest_deductible(self, digest_type):
        self.l.debug("get_digest_deductible")

        if self.does_method_exist(f"get_{digest_type}_allowance_actual"):
            allowance = self.call_method(f"get_{digest_type}_allowance_actual")
            if self.does_method_exist(f"get_{digest_type}_expenses_actual"):
                expenses = self.call_method(f"get_{digest_type}_expenses_actual")
                deductible = max(allowance, expenses)
            else:
                deductible = allowance
        else:
            deductible = self.call_method(f"get_{digest_type}_allowance")
        self.l.debug(f"deductible: {deductible}")
        return deductible

    def get_digest_deductible_gbp(self, digest_type):
        self.l.debug("get_digest_deductible_gbp")
        self.l.debug(f"digest_type: {digest_type}")
        deductible = self.get_digest_deductible(digest_type)
        self.l.debug(f"deductible: {deductible}")
        return self.gbp(deductible).strip()

    def get_digest_deductible_label(self, digest_type):
        self.l.debug("get_digest_deductible_label")
        self.l.debug(f"digest_type: {digest_type}")
        if self.does_method_exist(f"get_{digest_type}_allowance_actual"):
            allowance = self.call_method(f"get_{digest_type}_allowance_actual")
            if self.does_method_exist(f"get_{digest_type}_expenses_actual"):
                expenses = self.call_method(f"get_{digest_type}_expenses_actual")
            else:
                expenses = 0
            if allowance > expenses:
                deductible_label = "allowance"
            else:
                deductible_label = "expenses"
        else:
            deductible_label = "allowance"
        self.l.debug(f"deductible_label: {deductible_label}")
        return deductible_label

    def get_digest_income(self, digest_type):
        amount = self.call_method(f"get_{digest_type}_income")
        self.l.debug(f"amount: {amount}")
        return amount

    def get_digest_income_gbp(self, digest_type):
        self.l.debug("get_digest_income_gbp")
        self.l.debug(f"digest_type: {digest_type}")
        amount = self.get_digest_income(digest_type)
        return self.gbp(amount).strip()

    def get_digest_taxible_gbp(self, digest_type):
        self.l.debug("get_digest_taxible_gbp")
        income = self.get_digest_income(digest_type)
        deductible = self.get_digest_deductible(digest_type)
        taxible = max(0, income - deductible)
        return self.gbp(taxible).strip()

    def get_digest_type_categories(self) -> dict:
        person_code = self.person_code
        return {
            "savings": " INT ",
            "dividends": " DIV ",
            "trading": " SES ",
            "property": " UKP ",
        }

    def get_disability_and_foreign_service_deduction(self):
        return self.gbpb(0)

    def get_dividends_allowance(self):
        return self.constants.get_dividends_allowance()

    def get_dividends_allowance_gbp(self):
        return self.gbp(self.get_dividends_allowance())

    def get_dividends_basic_rate(self):
        return self.constants.get_dividends_basic_rate()

    def get_dividends_digest(self):
        self.l.debug("get_dividends_digest")
        return self.get_digest_by_type("dividends")

    def get_dividends_from_uk_companies(self):
        person_code = self.person_code
        tax_year = self.tax_year
        return self.get_year_category_total(
            tax_year, f"HMRC {person_code} INC Dividends from UK companies"
        )

    def get_dividends_income(self) -> Decimal:
        person_code = self.person_code
        tax_year = self.tax_year
        category_like = f"HMRC {person_code} DIV income: "
        dividends_income = self.transactions.fetch_total_by_tax_year_category_like(
            tax_year, category_like
        )
        return self.round_down(dividends_income, 0)

    def get_dividends_income_gbp(self):
        return self.gbpb(self.get_dividends_income())

    def get_dividends_tax_digest(self):
        self.l.debug("get_dividends_tax_digest")
        if not self.are_there_dividends_transactions():
            return ""
        income = self.get_dividends_income()
        dividends_allowance = self.get_dividends_allowance()
        taxable_dividends = max(0, income - dividends_allowance)
        taxable_dividends_gbp = self.gbp(taxable_dividends).strip()
        parts = [f"taxable dividends: {taxable_dividends_gbp}"]
        unused_allowance = self.unused_allowance
        taxable_amount = max(0, taxable_dividends - unused_allowance)
        (tax, unused_allowance) = self.calculate_dividends_tax(income, unused_allowance)
        self.unused_allowance = unused_allowance
        tax_gbp = self.gbp(tax).strip()
        unused_allowance_gbp = self.gbp(unused_allowance).strip()
        parts.append(f"unused personal allowance: {unused_allowance_gbp}")
        parts.append(f"taxable amount: {taxable_amount}")
        parts.append(f"tax: {tax_gbp}")
        return "\n" + " | ".join(parts)

    def get_earlier_year_tax_year_to_be_taxed(self):
        return self.gbpb(0)

    def get_earlier_years__losses(self):
        return self.gbpb(0)

    def get_electric_charge_point_allowance(self):
        return self.gbpb(0)

    def get_electric_charge_point_allowance_gbp(self):
        return self.gbpb(0)

    def get_email_address(self):
        return self.person.get_email_address()

    def get_estimated_underpaid_tax_for_this_tax_year_paye_gbp(self):
        return self.gbpb(0)

    def get_exempt_overseas_employee_contributions(self):
        return self.gbpb(0)

    def get_exemptions_for_amounts_entered_in_box_4(self):
        return self.gbpb(0)

    def get_final_digest(self):
        self.l.debug("get_final_digest")
        income_gbp = self.get_total_taxable_income_gbp().strip()
        parts = [f"TOTAL taxable income: {income_gbp}"]
        tax = self.get_total_tax_due_gbp().strip()
        parts.append(f"total tax: {tax}")
        payment_by_31st_jan = self.get_total_to_add_to_sa_account_due_by_31st_january()
        payment_by_31st_jan_gbp = self.gbp(payment_by_31st_jan).strip()
        parts.append(f"payment by 31st January: {payment_by_31st_jan_gbp}")
        return "\n" + " | ".join(parts)

    def get_first_name(self):
        return self.person.get_first_name()

    def get_first_payment_on_account_for_next_year(self) -> Decimal:
        values = [self.get_income_tax(), self.get_class_4_nics_due()]
        total = financial_helpers.sum_values(values)
        first_payment_on_account_for_next_year = total / 2
        return first_payment_on_account_for_next_year

    def get_first_payment_on_account_for_next_year_gbp(self) -> str:
        payment = self.get_first_payment_on_account_for_next_year()
        return self.gbpb(payment)

    def get_for_how_many_children__cb_(self):
        return self.gbpb(0)

    def get_foreign_dividends(self):
        person_code = self.person_code
        tax_year = self.tax_year
        return self.get_year_category_total(
            tax_year, f"HMRC {person_code} INC Foreign dividends"
        )

    def get_foreign_earnings_not_taxable_in_the_uk(self):
        return self.gbpb(0)

    def get_foreign_tax_paid_on_an_unauthorised_payment(self):
        return self.gbpb(0)

    def get_foreign_tax_paid_on_box_16(self):
        return self.gbpb(0)

    def get_foreign_tax_where_tax_credit_not_claimed(self):
        return self.gbpb(0)

    def get_freeport_allowance_for_property_gbp(self):
        return self.gbpb(0)

    def get_freeport_allowance_for_trading_gbp(self):
        return self.gbpb(0)

    def get_gains_from_voided_isas(self):
        return self.gbpb(0)

    def get_gift_aid_payments(self):
        return self.gbpb(0)

    def get_gift_aid_payments_after_end_of_tax_year(self):
        return self.gbpb(0)

    def get_gift_aid_payments_from_previous_tax_year_(self):
        return self.gbpb(0)

    def get_gift_aid_payments_to_non_uk_charities_in_box_6(self):
        return self.gbpb(0)

    def get_gilt_interest_after_tax_taken_off(self):
        return self.gbpb(0)

    def get_goods_or_services_for_your_own_use_gbp(self):
        return ""

    def get_gross_amount_before_tax(self):
        return self.gbpb(0)

    def get_higher_rate_threshold(self):
        return self.constants.get_higher_rate_threshold()

    def get_higher_tax_rate(self):
        self.l.debug("get_higher_tax_rate")
        higher_tax_rate = self.constants.get_higher_tax_rate()
        return higher_tax_rate

    def get_hmrc_allowance(self):
        self.l.debug("get_hmrc_allowance")
        personal_allowance = self.get_personal_allowance()
        self.l.debug(f"personal_allowance: {personal_allowance}")
        allowance_enlargement = self.get_marriage_allowance_recipient_amount()
        # allowance_enlargement=0
        self.l.debug(f"allowance_enlargement: {allowance_enlargement}")
        allowance_reduction = self.get_marriage_allowance_donor_amount()
        self.l.debug(f"allowance_reduction: {allowance_reduction}")
        hmrc_allowance = (
            personal_allowance + allowance_enlargement - allowance_reduction
        )
        self.l.debug(f"hmrc_allowance: {hmrc_allowance}")
        return hmrc_allowance

    def get_hmrc_businesses(self):
        hmrc_businesses = []
        person_code = self.person.code
        tax_year = self.tax_year
        category_like = f"HMRC {person_code} SES income: "
        where = f'"Tax year"="{tax_year}" AND "Category" LIKE "{category_like}%"'
        query = (
            self.transactions.query_builder()
            .select_raw("DISTINCT Category")
            .where(where)
            .build()
        )
        rows = self.sql.fetch_all(query)
        start_position = len(category_like)
        for row in rows:
            business_name = row[0][start_position:]
            hmrc_business = HMRC_Businesses(business_name)
            hmrc_businesses.append(hmrc_business)
        return hmrc_businesses

    def get_hmrc_calculation(self) -> str:
        self.l.debug("get_hmrc_calculation")
        hmrc_calculation = HMRC_Calculation(self)
        return hmrc_calculation.get_output()

    def get_hmrc_total_income(self) -> Decimal:
        self.l.debug("get_hmrc_total_income")
        total_income_received = self.get_hmrc_total_income_received()
        self.l.debug(f"total_income_received: {total_income_received}")
        hmrc_allowance = self.get_hmrc_allowance()
        self.l.debug(f"hmrc_allowance: {hmrc_allowance}")
        hmrc_total_income = max(0, total_income_received - hmrc_allowance)
        self.l.debug(f"hmrc_total_income: {hmrc_total_income}")

        return hmrc_total_income

    def get_hmrc_total_income_received(self) -> Decimal:
        values = [
            self.get_trading_profit(),
            self.get_property_profit(),
            self.get_savings_income(),
            self.get_dividends_income(),
        ]
        return financial_helpers.sum_values(values)

    def get_how_many_businesses(self):
        hmrc_businesses = self.get_hmrc_businesses()
        return len(hmrc_businesses)

    def get_how_many_employments(self):
        person_code = self.person.code
        tax_year = self.tax_year
        query = (
            self.transactions.query_builder()
            .select_raw("COUNT(DISTINCT Category)")
            .where(
                f'"Tax year"="{tax_year}" AND "Category" LIKE "HMRC {person_code} EMP%"'
            )
            .build()
        )
        how_many = self.sql.fetch_one_value(query)
        return how_many

    def get_how_many_partnerships(self):
        return 0

    def get_how_many_properties_do_you_rent_out(self):
        person_code = self.person.code
        tax_year = self.tax_year
        query = (
            self.transactions.query_builder()
            .select_raw("COUNT(DISTINCT Category)")
            .where(
                f'"Tax year"="{tax_year}" AND "Category" LIKE "HMRC {person_code} UKP income%"'
            )
            .build()
        )
        how_many = self.sql.fetch_one_value(query)
        return how_many

    def get_how_many_self_employed_businesses_did_you_have(self) -> int:
        person_code = self.person.code
        tax_year = self.tax_year
        query = (
            self.transactions.query_builder()
            .select_raw("COUNT(DISTINCT Category)")
            .where(
                f'"Tax year"="{tax_year}" AND "Category" LIKE "HMRC {person_code} SES income%"'
            )
            .build()
        )
        how_many = self.sql.fetch_one_value(query)
        return how_many

    def get_how_many_years_policy_was_last_held_or_received_gain(self):
        return self.gbpb(0)

    def get_how_much_child_benefit__cb__received(self):
        return 0.0

    def get_how_would_you_like_to_record_your_expenses(self):
        return "As a single total value"

    def get_if_you_filled_in_boxes_23_and_24_enter_your_name(self):
        return self.gbpb(0)

    def get_income__trading_allowance__claim_back_cis(self):
        return False

    def get_income__trading_allowance__volunteer_c2_nics(self):
        trading_income = self.get_trading_income()
        trading_allowance = self.get_trading_allowance_actual()
        pay_voluntarily_nics = self.do_you_want_to_pay_class_2_nics_voluntarily()
        return trading_income <= trading_allowance and pay_voluntarily_nics

    def get_income_tax(self) -> Decimal:
        self.l.debug("get_income_tax")
        non_savings_income = self.get_non_savings_income()
        self.l.debug(f"non_savings_income: {non_savings_income}")
        savings_income = self.get_savings_income()
        self.l.debug(f"savings_income: {savings_income}")
        dividends_income = self.get_dividends_income()
        self.l.debug(f"dividends_income: {dividends_income}")
        tax_free_allowance = self.get_hmrc_allowance()
        (non_savings_tax, available_allowance) = self.calculate_tax(
            non_savings_income, tax_free_allowance
        )
        self.l.debug(f"non_savings_tax: {non_savings_tax}")
        self.l.debug(f"available_allowance: {available_allowance}")
        (savings_tax, available_allowance) = self.calculate_savings_tax(
            savings_income, available_allowance
        )
        self.l.debug(f"savings_tax: {savings_tax}")
        self.l.debug(f"available_allowance: {available_allowance}")
        (dividends_tax, available_allowance) = self.calculate_dividends_tax(
            dividends_income, available_allowance
        )
        self.l.debug(f"dividends_tax: {dividends_tax}")
        self.l.debug(f"available_allowance: {available_allowance}")
        income_tax = non_savings_tax + savings_tax + dividends_tax
        self.l.debug(f"income_tax: {income_tax}")
        return income_tax

    def get_income_tax_gbp(self):
        return self.gbp(self.get_income_tax())

    def get_increase_in_tax_due_to_earlier_years_adjustments_gbp(self):
        return self.gbpb(0)

    def get_jobseeker_s_allowance_gbp(self):
        self.gbpb(0)

    def get_last_name(self):
        return self.person.get_last_name()

    def get_legal_or_management_and_other_professional_fees(self) -> Decimal:
        category_like = "UKP expense: legal"
        legal_or_management_and_other_professional_fees = (
            self.get_total_transactions_by_category_like(category_like)
        )
        return self.round_up(legal_or_management_and_other_professional_fees, 0)

    def get_legal_or_management_and_other_professional_fees_gbp(self):
        return self.gbpb(self.get_legal_or_management_and_other_professional_fees())

    def get_lifetime_allowance_tax_paid_by_your_pension_scheme(self):
        return self.gbpb(0)

    def get_loans_written_off(self):
        return self.gbpb(0)

    def get_local_authority_or_other_register(self):
        return self.gbpb(0)

    def get_loss_brought_forward_against_this_year_s_profits_gbp(self):
        return self.gbpb(0)    

    def get_loss_brought_forward_set_off_against_profits_gbp(self):
        return self.gbpb(0)    

    def get_loss_carried_back_prior_years_set_off_income_cg_gbp(self):
        return self.gbpb(0)    

    def get_loss_set_off_against_other_income_this_tax_year_gbp(self):
        return self.gbpb(0)    

    def get_loss_to_take_forward_post_set_offs_unused_losses_gbp(self):
        return self.gbpb(0)    

    def get_loss_to_carry_forward__inc_unused_losses_gbp(self):
        return self.gbpb(0)    

    def get_losses_brought_forward_and_set_off_gbp(self):
        return self.gbpb(0)    

    def get_lump_sum_pension___available_lifetime_allowance(self):
        return self.gbpb(0)

    def get_lump_sums_employer_financed_retirement_benefits_scheme(self):
        return self.gbpb(0)

    def get_maintenance_payments(self):
        return self.gbpb(0)

    def get_marital_status(self):
        return self.person.get_marital_status()

    def get_marriage_allowance_digest(self):
        self.l.debug("get_marriage_allowance_digest")
        if not self.is_married():
            return ""
        marriage_allowance = self.get_marriage_allowance_donor_amount()
        self.l.debug(f"marriage_allowance: {marriage_allowance}")
        if marriage_allowance == 0:
            return ""
        transferred_to = self.spouse.get_name()
        marriage_allowance_gbp = self.gbp(marriage_allowance).strip()
        parts = [f"MARRIAGE ALLOWANCE: {marriage_allowance_gbp}"]
        parts.append(f"transferred to: {transferred_to}")
        return "\n" + " | ".join(parts)

    def get_marriage_allowance_donor_amount(self) -> Decimal:
        if not self.is_married():
            return Decimal(0)

        total_income = self.get_hmrc_total_income_received()

        personal_allowance = self.get_personal_allowance()

        if total_income > personal_allowance:
            return Decimal(0)

        spouse_total_income = self.get_spouse_total_income_received()
        if personal_allowance > spouse_total_income:
            return Decimal(0)

        higher_rate_threshold = self.get_higher_rate_threshold()
        if spouse_total_income > higher_rate_threshold:
            return Decimal(0)

        max_marriage_allowance = self.constants.get_marriage_allowance()

        return min(
            max_marriage_allowance,
            personal_allowance - total_income,
        )

    def get_marriage_allowance_donor_amount_gbp(self) -> str:
        return self.gbpb(self.get_marriage_allowance_donor_amount())

    @lru_cache(maxsize=None)
    def get_marriage_allowance_recipient_amount(self) -> Decimal:
        self.l.debug("get_marriage_allowance_recipient_amount")
        if not self.is_married():
            return Decimal(0)
        spouse_hmrc = self.get_spouse_hmrc()
        self.l.debug("Disabling debug for spouse HMRC instance")
        spouse_hmrc.disable_debug()
        marriage_allowance_recipient_amount = (
            spouse_hmrc.get_marriage_allowance_donor_amount()
        )
        spouse_hmrc.enable_debug()
        self.l.debug("Enabled debug for spouse HMRC instance")
        self.l.debug(
            f"marriage_allowance_recipient_amount: {marriage_allowance_recipient_amount}"
        )
        return marriage_allowance_recipient_amount

    def get_marriage_allowance_recipient_amount_gbp(self) -> str:
        return self.gbpb(self.get_marriage_allowance_recipient_amount())

    def get_marriage_date(self) -> str:
        if not self.is_married():
            return ""
        return self.spouse.get_uk_marriage_date()

    def get_married_people_s_surplus_allowance_you_can_have(self):
        return self.gbpb(0)

    def get_middle_name(self):
        return self.person.get_middle_name()

    def get_name_of_the_peson_you_ve_signed_for(self):
        return self.gbpb(0)

    def get_net_business_loss_for_tax_purposes(self):
        income = self.get_business_income()
        net_business_loss_for_tax_purposes = (
            min(0, income - self.get_trading_expenses_actual()) * -1
        )
        return net_business_loss_for_tax_purposes

    def get_net_business_loss_for_tax_purposes_gbp(self):
        return self.gbpb(self.get_net_business_loss_for_tax_purposes())

    def get_net_business_profit_for_tax_purposes(self):
        self.l.debug("get_net_business_profit_for_tax_purposes")
        income = self.get_business_income()
        if self.use_trading_allowance():
            self.l.debug("Using trading allowance")
            net_business_profit_for_tax_purposes = max(
                0, income - self.get_trading_allowance_actual()
            )
        else:
            self.l.debug("Using expenses")
            net_business_profit_for_tax_purposes = max(
                0, income - self.get_trading_expenses_actual()
            )
        return net_business_profit_for_tax_purposes

    def get_net_business_profit_for_tax_purposes_gbp(self):
        return self.gbpb(self.get_net_business_profit_for_tax_purposes())

    def get_net_loss(self):
        return min(0, self.get_bottom_line()) * -1

    def get_net_loss_gbp(self):
        return self.gbpb(self.get_net_loss())

    def get_net_profit(self):
        return max(0, self.get_bottom_line())

    def get_net_profit_gbp(self):
        return self.gbpb(self.get_net_profit())

    def get_nominee_s_address(self):
        return self.gbpb(0)

    def get_nominee_s_postcode(self):
        return self.gbpb(0)

    def get_non_deductible_loan_interest_letting_pship_investments(self):
        return self.gbpb(0)

    def get_non_lump_sum_pension___available_lifetime_allowance(self):
        return self.gbpb(0)

    def get_non_residential_finance_property_costs(self):
        return self.gbpb(0)

    def get_non_residential_finance_property_costs_gbp(self):
        return self.gbpb(0)

    def get_non_savings_income(self):
        self.l.debug("get_non_savings_income")
        values = [self.get_trading_profit(), self.get_property_profit()]
        non_savings_income = financial_helpers.sum_values(values)
        self.l.debug(f"non_savings_income: {non_savings_income}")
        return non_savings_income

    def get_not_applicable(self):
        return self.gbpb(0)

    def get_number_of_properties_rented_out(self):
        return self.gbpb(0)

    def get_number_of_years_policy_was_last_held_or_received_gain(self):
        return self.gbpb(0)

    def get_other_business_income_not_already_included(self):
        return 0

    def get_other_business_income_not_already_included_gbp(self):
        return self.gbpb(self.get_other_business_income_not_already_included())

    def get_other_business_income_not_included_as_trading_income(self):
        return 0

    def get_other_business_income_not_trading_income_gbp(self):
        return self.gbpb(
            self.get_other_business_income_not_included_as_trading_income()
        )

    def get_other_capital_allowances_gbp(self):
        return ""

    def get_other_dividends(self):
        person_code = self.person_code
        tax_year = self.tax_year
        return self.get_year_category_total(
            tax_year, f"HMRC {person_code} INC Other dividends"
        )

    def get_other_information_about_this_business(self):
        return ""

    def get_other_information_about_your_uk_property_income(self):
        return ""

    def get_other_property_expenses(self):
        return 0

    def get_other_property_expenses_gbp(self):
        return self.gbpb(self.get_other_property_expenses())

    def get_outstanding_debt_included_in_tax_code(self):
        return 0

    def get_outstanding_debt_included_in_tax_code_gbp(self):
        return self.gbp(self.get_outstanding_debt_included_in_tax_code())

    def get_overview(self) -> str:
        self.l.debug("get_overview")
        parts = self.get_overview_parts()
        return "\n".join(parts)

    def get_overview_parts(self) -> list:
        self.l.debug("get_overview_parts")
        steps = [
            "get_trading_digest",
            "get_property_digest",
            "get_savings_digest",
            "get_dividends_digest",
            "get_final_digest",
            "get_combined_tax_digest",
            "get_savings_tax_digest",
            "get_dividends_tax_digest",
            "get_marriage_allowance_digest",
        ]
        parts = []
        for step in steps:
            part = self.call_method(step)
            if part:
                parts.append(part)
        return parts

    def get_payments_to_a_retirement_annuity_contract(self):
        return 0

    def get_payments_to_a_retirement_annuity_contract_gbp(self):
        return self.gbpb(self.get_payments_to_a_retirement_annuity_contract())

    def get_payments_to_a_trade_union_for_death_benefits(self):
        return self.gbpb(0)

    def get_payments_to_an_overseas_pension_scheme(self):
        return 0

    def get_payments_to_an_overseas_pension_scheme_gbp(self):
        return self.gbpb(self.get_payments_to_an_overseas_pension_scheme())

    def get_payments_to_annuity_tax_relief_not_claimed(self):
        return 0

    def get_payments_to_employers_scheme_where_no_tax_deducted(self):
        return 0

    def get_payments_to_overseas_pension_scheme(self):
        return 0

    def get_payments_to_pension_schemes__relief_at_source(self) -> Decimal:
        person_code = self.person_code
        payments_to_pension_schemes = (
            self.transactions.fetch_total_by_tax_year_category_like(
                self.tax_year, f"HMRC {person_code} RLF pension"
            )
        )
        return payments_to_pension_schemes

    def get_payments_to_pension_schemes__relief_at_source__gbp(self):
        return self.gbpb(self.get_payments_to_pension_schemes__relief_at_source())

    def get_payments_to_your_employer_s_scheme(self):
        return 0

    def get_payments_to_your_employer_s_scheme_gbp(self):
        return self.gbpb(self.get_payments_to_your_employer_s_scheme())

    def get_pension_charges_due(self):
        return self.gbpb(0)

    def get_pension_contributions(self):
        person_code = self.person_code
        pension_contributions = self.transactions.fetch_total_by_tax_year_category(
            self.tax_year, f"HMRC {person_code} RLF pension contribution"
        )
        return pension_contributions

    def get_pension_scheme_tax_reference_number(self):
        return self.gbpb(0)

    def get_private_pensions_income(self):
        person_code = self.person_code
        tax_year = self.tax_year
        category_like = f"HMRC {person_code} PEN income: "
        return self.transactions.fetch_total_by_tax_year_category_like(
            tax_year, category_like
        )

    def get_private_pensions_income__other_than_state_pension_(self):
        return 0

    def get_person_name(self):
        return self.person.get_name()

    def get_personal_allowance(self):
        return self.constants.get_personal_allowance()

    def get_personal_allowance_gbp(self):
        return self.gbp(self.get_personal_allowance())

    def get_personal_savings_allowance(self):
        return self.constants.get_personal_savings_allowance()

    def get_please_give_any_other_information_about_this_business(self):
        return ""

    def get_post_cessation_receipts_amount(self):
        return self.gbpb(0)

    def get_post_cessation_trade_relief_and_certain_other_losses(self):
        return self.gbpb(0)

    def get_postgraduate_loan_repayment_due(self):
        return self.gbpb(0)

    def get_pre_incorporation_losses(self):
        return self.gbpb(0)

    def get_premiums_for_the_grant_of_a_lease(self):
        return self.gbpb(0)

    def get_premiums_for_the_grant_of_a_lease_gbp(self):
        return self.gbpb(0)

    def get_private_use_adjustment(self):
        return 0

    def get_private_use_adjustment_gbp(self):
        return self.gbpb(self.get_private_use_adjustment())

    def get_profit_or_loss_gbp(self):
        return self.gbpb(self.get_business_income())

    def get_property_adjustments_gbp(self):
        return self.gbpb(0)

    def get_property_allowance(self):
        actual_property_allowance = self.get_property_allowance_actual()
        actual_property_expenses = self.get_property_expenses_actual()
        if actual_property_allowance >= actual_property_expenses:
            return actual_property_allowance
        else:
            return 0

    def get_property_allowance_actual(self):
        return self.constants.get_property_income_allowance()

    def get_property_allowance_actual_gbp(self):
        return self.gbpb(self.get_property_allowance_actual())

    def get_property_allowance_gbp(self):
        property_allowance = self.get_property_allowance()
        return self.gbpb(property_allowance)

    def get_property_balancing_charges(self):
        return 0

    def get_property_balancing_charges_gbp(self):
        return self.gbpb(self.get_property_balancing_charges())

    def get_property_digest(self) -> str:
        self.l.debug("get_property_digest")
        return self.get_digest_by_type("property")

    def get_property_expenses(self):
        actual_property_allowance = self.get_property_allowance_actual()
        actual_property_expenses = self.get_property_expenses_actual()
        if actual_property_expenses > actual_property_allowance:
            return actual_property_expenses
        else:
            return 0

    def get_property_expenses_actual(self) -> Decimal:
        property_expenses = [
            self.get_rent__rates__insurance_and_ground_rents(),
            self.get_property_repairs_and_maintenance(),
            self.get_legal_or_management_and_other_professional_fees(),
        ]
        total_property_expenses = financial_helpers.sum_values(property_expenses)
        return total_property_expenses

    def get_property_expenses_actual_gbp(self):
        return self.gbpb(self.get_property_expenses_actual())

    def get_property_expenses_breakdown(self):
        person_code = self.person_code
        category_like = f"HMRC {person_code} UKP expense"
        return self._get_breakdown(category_like)

    def get_total_property_expenses_gbp(self):
        return self.gbpb(self.get_property_expenses())

    def get_property_income(self) -> Decimal:
        person_code = self.person_code
        tax_year = self.tax_year
        category_like = f"HMRC {person_code} UKP income"
        property_income = self.transactions.fetch_total_by_tax_year_category_like(
            tax_year, category_like
        )
        return Decimal(self.round_down(property_income))

    def get_property_income_breakdown(self):
        person_code = self.person_code
        category_like = f"HMRC {person_code} UKP income"
        return self._get_breakdown(category_like)

    def get_property_income_gbp(self) -> str:
        return self.gbpb(self.get_property_income())

    @lru_cache(maxsize=None)
    def get_property_profit(self):
        self.l.debug("get_property_profit")
        property_allowance = self.get_property_allowance_actual()
        self.l.debug(f"property_allowance: {property_allowance}")
        property_expenses = self.get_property_expenses_actual()
        self.l.debug(f"property_expenses: {property_expenses}")
        property_income = self.get_property_income()
        self.l.debug(f"property_income: {property_income}")
        property_outgo = max(property_allowance, property_expenses)
        self.l.debug(f"property_outgo: {property_outgo}")
        property_profit = max(0, property_income - property_outgo)
        self.l.debug(f"property_profit: {property_profit}")
        return property_profit

    def get_property_profit_gbp(self):
        return self.gbpb(self.get_property_profit())

    def get_property_reduction(self):
        actual_property_allowance = self.get_property_allowance_actual()
        actual_property_expenses = self.get_property_expenses_actual()
        return max(actual_property_expenses, actual_property_allowance)

    def get_property_repairs_and_maintenance(self) -> Decimal:
        category_like = "UKP expense: repairs and maintenance"
        repairs_and_maintenance = self.get_total_transactions_by_category_like(
            category_like
        )
        return self.round_up(repairs_and_maintenance, 0)

    def get_property_repairs_and_maintenance_gbp(self):
        return self.gbpb(self.get_property_repairs_and_maintenance())

    def get_property_taxable_profit_for_the_year(self):
        return self.get_adjusted_profit_for_the_year()

    def get_property_taxable_profit_for_the_year_gbp(self):
        return self.gbpb(self.get_property_taxable_profit_for_the_year())

    def get_qualifying_loan_interest_payable_in_the_year(self):
        return self.gbpb(0)

    def get_questions(self):
        report_type = self.report_type
        match report_type:
            case HMRC_Output.HMRC_CALCULATION:
                questions = HMRC_QuestionsByYear(
                    self.tax_year
                ).get_hmrc_calculation_questions()
            case HMRC_Output.HMRC_ONLINE_ANSWERS:
                questions = HMRC_QuestionsByYear(self.tax_year).get_online_questions()
            case HMRC_Output.HMRC_TAX_RETURN:
                questions = HMRC_QuestionsByYear(
                    self.tax_year
                ).get_printed_form_questions()
            case _:
                raise ValueError(f"Unexpected report type: {report_type}")
        return questions

    def get_redundancy_payments(self):
        return self.gbpb(0)

    def get_refunded_or_off_set_income_tax(self):
        return self.gbpb(0)

    def get_registered_blind_(self):
        return False

    def get_relief_at_source_pension_payments_to_ppr_gbp(self):
        return self.gbpb(self.get_payments_to_pension_schemes__relief_at_source())

    def get_relief_claimed_on_a_qualifying_distribution(self):
        return self.gbpb(0)

    def get_relief_now_for_following_year_trade_losses(self):
        return self.gbpb(0)

    def get_rent__rates__insurance_and_ground_rents(self) -> Decimal:
        category_like = "UKP expense: rent, rates"
        rent_rates_etc = self.get_total_transactions_by_category_like(category_like)
        return self.round_up(rent_rates_etc, 0)

    def get_rent__rates__insurance_and_ground_rents_gbp(self):
        return self.gbpb(self.get_rent__rates__insurance_and_ground_rents())

    def get_rent_a_room_exempt_amount(self):
        return self.gbpb(0)

    def get_rental_income_gbp(self):
        return self.gbpb(0)

    def get_rented_property_postcode(self):
        person_code = self.person.code
        tax_year = self.tax_year
        query = (
            self.transactions.query_builder()
            .select_raw("DISTINCT Category")
            .where(
                f'"Tax year"="{tax_year}"'
                + f' AND "Category" LIKE "HMRC {person_code} UKP income: rent received %"'
            )
            .build()
        )
        self.l.debug(f"query: {query}")
        category = self.sql.fetch_one_value(query)
        self.l.debug(f"category: {category}")
        prefix_length = len("HMRC B UKP income: rent received ")
        rented_property_postcode = category[prefix_length:]
        self.l.debug(f"rented_property_postcode: {rented_property_postcode}")
        return rented_property_postcode

    def get_residential_property_finance_costs(self):
        return self.gbpb(0)

    def get_residential_property_finance_costs_gbp(self):
        return self.gbpb(0)

    def get_reverse_premiums(self):
        return self.gbpb(0)

    def get_reverse_premiums_and_inducements_gbp(self):
        return self.gbpb(0)

    def get_revised_basic_rate_threshold(self):
        self.l.debug("get_revised_basic_rate_threshold")
        pension_payments = self.get_payments_to_pension_schemes__relief_at_source()
        self.l.debug(f"pension_payments: {pension_payments}")
        basic_rate_threshold = self.get_basic_rate_threshold()
        self.l.debug(f"basic_rate_threshold: {basic_rate_threshold}")
        revised_basic_rate_threshold = basic_rate_threshold + pension_payments
        self.l.debug(f"revised_basic_rate_threshold: {revised_basic_rate_threshold}")
        return revised_basic_rate_threshold

    def get_savings_allowance(self):
        return self.constants.get_personal_savings_allowance()

    def get_savings_allowance_gbp(self):
        savings_allowance = self.get_savings_allowance()
        return self.gbpb(savings_allowance)

    def get_savings_basic_rate(self):
        return self.constants.get_savings_basic_rate()

    def get_savings_digest(self):
        self.l.debug("get_savings_digest")
        return self.get_digest_by_type("savings")

    def get_savings_income(self) -> Decimal:
        person_code = self.person_code
        tax_year = self.tax_year
        category_like = f"HMRC {person_code} INT income"
        savings_income = self.transactions.fetch_total_by_tax_year_category_like(
            tax_year, category_like
        )
        return self.round_down(savings_income, 0)

    def get_savings_income_breakdown(self):
        person_code = self.person_code
        category_like = f"HMRC {person_code} INT income"
        return self._get_breakdown(category_like)

    def get_savings_income_gbp(self) -> str:
        return self.gbpb(self.get_savings_income())

    def get_savings_nil_band(self):
        return self.constants.get_savings_nil_band()

    def get_savings_tax_digest(self):
        self.l.debug("get_savings_tax_digest")
        if not self.are_there_savings_transactions():
            return ""
        taxable_savings = self.get_taxable_savings()
        self.l.debug(f"taxable_savings: {taxable_savings}")
        unused_allowance = self.unused_allowance
        self.l.debug(f"unused_allowance: {unused_allowance}")
        taxable_amount = max(0, taxable_savings - unused_allowance)
        self.l.debug(f"taxable_amount: {taxable_amount}")
        taxable_amount_gbp = self.gbp(taxable_amount).strip()
        income = self.get_savings_income()
        self.l.debug(f"income: {income}")
        (tax, new_unused_allowance) = self.calculate_savings_tax(
            income, unused_allowance
        )
        self.l.debug(f"new_unused_allowance: {new_unused_allowance}")
        self.unused_allowance = new_unused_allowance
        tax_gbp = self.gbp(tax).strip()
        unused_allowance_gbp = self.gbp(unused_allowance).strip()
        taxable_savings_gbp = self.gbp(taxable_savings).strip()
        parts = [
            f"taxable savings: {taxable_savings_gbp}",
            f"unused personal allowance: {unused_allowance_gbp}",
            f"taxable amount: {taxable_amount_gbp}",
            f"tax: {tax_gbp}",
        ]
        return "\n" + " | ".join(parts)

    def get_seafarers__earnings_deduction(self):
        return self.gbpb(0)

    def get_second_payment_on_account_for_next_year_gbp(self) -> str:
        payment = self.get_first_payment_on_account_for_next_year()
        return self.gbpb(payment)

    def get_share_schemes_taxable_amount(self):
        return self.gbpb(0)

    def get_shares_under_the_seed_enterprise_investment_scheme(self):
        return self.gbpb(0)

    def get_should_your_spouse_get_your_surplus_allowance(self):
        return self.gbpb(0)

    def get_signature_to_authorise_nominee(self):
        return self.gbpb(0)

    def get_signing_capacity_if_signing_for_someone_else(self):
        return self.gbpb(0)

    def get_small_balance_unrelieved_expenditure_allowance_gbp(self):
        return ""

    def get_small_profits_threshold(self):
        return self.constants.get_small_profits_threshold()

    def get_spouse_code(self):
        if not self.is_married():
            return ""
        return self.person.get_spouse_code()

    @lru_cache(maxsize=None)
    def get_spouse_hmrc(self):
        spouse_code = self.get_spouse_code()
        tax_year = self.tax_year
        self.l.debug(f"Getting HMRC instance for spouse: {spouse_code}")
        spouse_hmrc = HMRC(spouse_code, tax_year)
        return spouse_hmrc

    @lru_cache(maxsize=None)
    def get_spouse_total_income_received(self) -> Decimal:
        spouse_hmrc = self.get_spouse_hmrc()
        spouse_total_income_received = spouse_hmrc.get_hmrc_total_income_received()
        return spouse_total_income_received

    def get_starting_rate_limit_for_savings(self):
        return self.constants.get_starting_rate_limit_for_savings()

    def get_taxable_benefits_income(self):
        person_code = self.person_code
        tax_year = self.tax_year
        category_like = f"HMRC {person_code} BEN income: "
        return self.transactions.fetch_total_by_tax_year_category_like(
            tax_year, category_like
        )

    def get_state_pension(self):
        return 0

    def get_state_pension_lump_sum(self):
        return 0

    def get_stock_dividends(self):
        return self.gbpb(0)

    def get_structures_and_buildings_allowance(self):
        return self.gbpb(0)

    def get_structures_and_buildings_allowance_gbp(self):
        return ""

    def get_student_loan_repayment_due(self):
        return self.gbpb(0)

    def get_subscriptions_for_enterprise_investment_scheme_shares(self):
        return self.gbpb(0)

    def get_subscriptions_for_venture_capital_trust_shares(self):
        return self.gbpb(0)

    def get_tax_adjustments_gbp(self):
        return self.gbpb(0)

    def get_tax_advisor_s_address_and_postcode(self):
        return self.gbpb(0)

    def get_tax_advisor_s_name(self):
        return self.gbpb(0)

    def get_tax_advisor_s_phone_number(self):
        return self.gbpb(0)

    def get_tax_advisor_s_reference(self):
        return self.gbpb(0)

    def get_tax_avoidance_scheme_reference_number(self):
        return self.gbpb(0)

    def get_tax_due_on_untaxed_uk_interest(self):
        personal_allowance = self.get_personal_allowance()
        personal_savings_allowance = self.get_personal_savings_allowance()
        starting_rate_limit_for_savings = self.get_starting_rate_limit_for_savings()
        total_allowances = (
            personal_allowance
            + personal_savings_allowance
            + starting_rate_limit_for_savings
        )
        total_income = self.get_hmrc_total_income_received()
        untaxed_uk_interest = self.get_untaxed_uk_interest()
        non_interest_income = total_income - untaxed_uk_interest
        interest_free_allowance = max(0, total_allowances - non_interest_income)
        taxable_savings = max(0, untaxed_uk_interest - interest_free_allowance)
        savings_basic_rate = self.get_savings_basic_rate()
        tax_due_on_untaxed_uk_interest = taxable_savings * savings_basic_rate
        return tax_due_on_untaxed_uk_interest

    def get_tax_paid_on_overseas_transfer_charge(self):
        return self.gbpb(0)

    def get_tax_taken_off(self):
        return self.gbpb(0)

    def get_tax_taken_off_any_income_in_box_20(self):
        return self.gbpb(0)

    def get_tax_taken_off_box_11(self):
        return 0

    def get_tax_taken_off_box_9(self):
        return 0

    def get_tax_taken_off_boxes_3_to_5(self):
        return self.gbpb(0)

    def get_tax_taken_off_foreign_dividends(self):
        return 0

    def get_tax_taken_off_gain_in_box_8(self):
        return self.gbpb(0)

    def get_tax_taken_off_incapacity_benefit_in_box_13(self):
        return 0

    def get_tax_year_expected_advantage_arises(self):
        return self.gbpb(0)

    def get_tax_year_for_which_you_re_claiming_relief_in_box_3_(self):
        return self.gbpb(0)

    def get_taxable_by_digest_type(self, digest_type):
        self.l.debug("get_taxable_by_digest_type")
        self.l.debug(f"digest_type: {digest_type}")
        amount = self.call_method(f"get_taxable_{digest_type}")
        self.l.debug(f"amount: {amount}")
        return self.gbp(amount).strip()

    def get_taxable_dividends(self):
        dividends_allowance = self.get_dividends_allowance()
        dividends_income = self.get_dividends_income()
        taxable_dividends = max(0, dividends_income - dividends_allowance)
        return taxable_dividends

    def get_taxable_incapacity_benefit(self):
        return 0

    def get_taxable_income(self):
        self.l.debug("get_taxable_income")
        values = [
            self.get_trading_profit(),
            self.get_property_profit(),
            self.get_savings_income(),
            self.get_dividends_income(),
        ]
        taxable_income = financial_helpers.sum_values(values)
        self.l.debug(f"taxable_income: {taxable_income}")
        return taxable_income

    def get_taxable_lump_sums(self):
        return self.gbpb(0)

    def get_taxable_profits_or_net_loss__before_set_offs__gbp(self):
        return self.gbpb(self.get_net_business_profit_for_tax_purposes())

    def get_taxable_savings(self):
        savings_allowance = self.get_savings_allowance()
        savings_income = self.get_savings_income()
        taxable_savings = max(0, savings_income - savings_allowance)
        return taxable_savings

    def get_taxable_savings_gbp(self):
        return self.gbpb(self.get_taxable_savings())

    def get_taxable_short_service_refund__overseas_only_(self):
        return self.gbpb(0)

    def get_taxed_uk_interest(self):
        person_code = self.person_code
        tax_year = self.tax_year
        return self.get_year_category_total(
            tax_year, f"HMRC {person_code} INT income: interest UK taxed"
        )

    def get_taxed_uk_interest_after_tax_has_been_taken_off_gbp(self):
        return self.gbpb(0)

    def get_taxed_uk_interest_gbp(self):
        taxed_uk_interest = self.get_taxed_uk_interest()
        return self.gbpb(taxed_uk_interest)

    def get_taxpayer_residency_status(self):
        return self.person.get_taxpayer_residency_status()

    def get_tc_please_give_any_other_information_in_this_space(self):
        return ""

    def get_total_amount_of_allowable_expenses(self):
        return 0

    def get_total_balancing_charges_gbp(self):
        return ""

    def get_total_construction_industry_scheme__cis__deductions(self):
        return self.gbpb(0)

    def get_total_income__excluding_tax_free_savings__gbp(self) -> str:
        if not self.are_you_claiming_marriage_allowance():
            return ""
        trading_income_gbp = self.gbp(self.get_trading_income())
        property_income_gbp = self.gbp(self.get_property_income())
        t_and_p_gbp = self.gbp(self.get_total_income_excluding_tax_free_savings())
        return f"{t_and_p_gbp} = {trading_income_gbp} (trading) + {property_income_gbp} (property)"

    def get_total_income_excluding_tax_free_savings(self):
        total_income = self.get_hmrc_total_income_received()
        savings_income = self.get_savings_income()
        return total_income - savings_income

    def get_total_income_gbp(self):
        return self.gbpb(self.get_hmrc_total_income_received())

    def get_total_of_any__one_off__payments_in_box_1(self):
        my_payments = self.transactions.fetch_total_by_tax_year_category(
            self.tax_year, "HMRC S pension contribution"
        )
        hmrc_contribution = self.transactions.fetch_total_by_tax_year_category(
            self.tax_year, "HMRC S pension tax relief"
        )
        return my_payments + hmrc_contribution

    def get_total_of_any__one_off__payments_in_box_5(self):
        return self.gbpb(0)
    
    def get_total_of_any_other_taxable_state_pensions_and_benefits_gbp(self):
        return self.gbpb(self.get_taxable_benefits_income())

    def get_total_of_one_off_payments_gbp(self):
        return self.get_relief_at_source_pension_payments_to_ppr_gbp()

    def get_total_rents_and_other_income_from_property(self):
        return self.get_property_income()

    def get_total_rents_and_other_income_from_property_gbp(self):
        return self.gbpb(self.get_total_rents_and_other_income_from_property())

    def get_total_tax_due(self):
        self.l.debug("get_total_tax_due")
        income_tax = self.get_income_tax()
        class_2_nics = self.get_class_2_nics_due()
        self.l.debug(f"class_2_nics: {class_2_nics}")
        class_4_nics = self.get_class_4_nics_due()
        self.l.debug(f"class_4_nics: {class_4_nics}")
        total_tax_due = income_tax + class_2_nics + class_4_nics
        self.l.debug(f"total_tax_due: {total_tax_due}")
        return total_tax_due

    def get_total_tax_due_gbp(self) -> str:
        return self.gbpb(self.get_total_tax_due())

    def get_total_tax_overpaid(self):
        return self.gbpb(0)

    def get_total_taxable_income(self):
        self.l.debug("get_total_taxable_income")
        values = [
            self.get_trading_profit(),
            self.get_property_profit(),
            self.get_taxable_savings(),
            self.get_taxable_dividends(),
        ]
        total_taxable_income = financial_helpers.sum_values(values)
        self.l.debug(f"total_taxable_income: {total_taxable_income}")
        return total_taxable_income

    def get_total_taxable_income_gbp(self):
        return self.gbp(self.get_total_taxable_income())

    def get_total_taxable_profits_from_this_business(self):
        net_business_profit_for_tax_purposes = (
            self.get_net_business_profit_for_tax_purposes()
        )
        other_business_income_not_already_included = (
            self.get_other_business_income_not_already_included()
        )
        loss_brought_forward_set_off_against_profits = (
            self.get_trading_loss_brought_forward_set_off_against_profits()
        )
        total_taxable_profits_from_this_business = (
            net_business_profit_for_tax_purposes
            + other_business_income_not_already_included
            - loss_brought_forward_set_off_against_profits
        )
        return total_taxable_profits_from_this_business

    def get_total_taxable_profits_from_this_business_gbp(self):
        return self.gbpb(self.get_total_taxable_profits_from_this_business())

    def get_total_to_add_to_sa_account_due_by_31st_january(self):
        values = [
            self.get_total_tax_due(),
            self.get_first_payment_on_account_for_next_year(),
        ]
        total_amounts = financial_helpers.sum_values(values)
        return total_amounts

    def get_total_to_add_to_sa_account_due_by_31st_january_gbp(self):
        total = self.get_total_to_add_to_sa_account_due_by_31st_january()
        return self.gbpb(total)

    def get_total_transactions_by_category_like(self, category_like) -> Decimal:
        person_code = self.person_code
        tax_year = self.tax_year
        category_like = f"HMRC {person_code} {category_like}"
        total = self.transactions.fetch_total_by_tax_year_category_like(
            tax_year, category_like
        )
        return total

    def get_total_uk_property_income_gbp(self):
        return self.get_property_income()

    def get_total_unused_losses_carried_forward(self):
        return self.gbpb(0)

    def get_tr_please_give_any_other_information_in_this_space(self):
        return ""

    def get_trading_allowance(self):
        actual_trading_allowance = self.get_trading_allowance_actual()
        actual_trading_expenses = self.get_trading_expenses_actual()
        if actual_trading_allowance >= actual_trading_expenses:
            return actual_trading_allowance
        else:
            return 0

    def get_trading_allowance_actual(self):
        self.l.debug("get_trading_allowance_actual")
        trading_income_allowance = self.constants.get_trading_income_allowance()
        self.l.debug(f"trading_income_allowance: {trading_income_allowance}")
        return trading_income_allowance

    def get_trading_allowance_actual_gbp(self):
        return self.gbpb(self.get_trading_allowance_actual())

    def get_trading_allowance_gbp(self):
        trading_allowance = self.get_trading_allowance()
        return self.gbpb(trading_allowance)

    def get_trading_balancing_charges(self):
        return 0

    def get_trading_balancing_charges_gbp(self):
        return self.gbpb(self.get_trading_balancing_charges())

    def get_trading_digest(self) -> str:
        self.l.debug("get_trading_digest")
        return self.get_digest_by_type("trading")

    def get_trading_expenses(self):
        actual_trading_allowance = self.get_trading_allowance_actual()
        actual_trading_expenses = self.get_trading_expenses_actual()
        if actual_trading_expenses > actual_trading_allowance:
            return actual_trading_expenses
        else:
            return 0

    def get_trading_expenses_actual(self) -> Decimal:
        self.l.debug("get_trading_expenses_actual")
        if self.get_how_many_self_employed_businesses_did_you_have() > 1:
            raise ValueError("More than one business. Review the code")
        person_code = self.person_code
        tax_year = self.tax_year
        category_like = f"HMRC {person_code} SES expense"
        trading_expenses_actual = (
            self.transactions.fetch_total_by_tax_year_category_like(
                tax_year, category_like
            )
        )
        self.l.debug(f"trading_expenses_actual: {trading_expenses_actual}")
        return self.round_up(trading_expenses_actual)

    def get_trading_expenses_actual_gbp(self):
        return self.gbpb(self.get_trading_expenses_actual())

    def get_trading_expenses_breakdown(self):
        person_code = self.person_code
        category_like = f"HMRC {person_code} SES expense"
        return self._get_breakdown(category_like)

    def get_trading_expenses_gbp(self):
        return self.gbpb(self.get_trading_expenses())

    def get_trading_income(self) -> Decimal:
        if self.get_how_many_self_employed_businesses_did_you_have() > 1:
            raise ValueError("More than one business. Review the code")
        person_code = self.person_code
        tax_year = self.tax_year
        category_like = f"HMRC {person_code} SES income"
        trading_income = self.transactions.fetch_total_by_tax_year_category_like(
            tax_year, category_like
        )
        return self.round_down(trading_income)

    def get_trading_income__turnover__gbp(self) -> str:
        return self.get_trading_income_gbp()

    def get_trading_income_breakdown(self):
        person_code = self.person_code
        category_like = f"HMRC {person_code} SES income"
        return self._get_breakdown(category_like)

    def get_trading_income_gbp(self) -> str:
        return self.gbpb(self.get_trading_income())

    def get_trading_income_was_below__85k__total_expenses_in_box_20(self):
        return "See box 20"

    def get_trading_loss(self):
        trading_loss = max(
            0, self.get_trading_expenses_actual() - self.get_trading_income()
        )
        return trading_loss

    def get_trading_loss_brought_forward_against_this_year_s_profits_gbp(self):
        return self.gbpb(0)

    def get_trading_loss_brought_forward_set_off_against_profits(self):
        return 0

    def get_trading_loss_brought_forward_set_off_against_profits_gbp(self):
        return self.gbpb(0)

    def get_trading_loss_carried_back_prior_years_set_off_income_cg_gbp(self):
        return self.gbpb(0)

    def get_trading_loss_gbp(self):
        return self.gbpb(self.get_trading_loss())

    def get_trading_loss_set_off_against_income(self):
        return self.gbpb(0)

    def get_trading_loss_set_off_against_other_income_this_tax_year(self):
        return 0

    def get_trading_loss_set_off_against_other_income_this_tax_year_gbp(self):
        return self.gbpb(
            self.get_trading_loss_set_off_against_other_income_this_tax_year()
        )

    def get_trading_loss_to_carry_forward(self):
        return self.gbpb(0)

    def get_trading_loss_to_carry_forward__inc_unused_losses_gbp(self):
        return self.gbpb(0)

    def get_trading_loss_to_take_forward_post_set_offs_unused_losses_gbp(self):
        return self.gbpb(0)

    def get_trading_losses_brought_forward_and_set_off_gbp(self):
        return self.gbpb(0)

    def get_trading_outgo(self):
        self.l.debug("get_trading_outgo")
        if self.use_trading_allowance():
            trading_allowance = self.get_trading_allowance_actual()
        else:
            trading_allowance = 0
        self.l.debug(f"trading_allowance: {trading_allowance}")
        if self.deduct_trading_expenses():
            trading_expenses = self.get_trading_expenses_actual()
        else:
            trading_expenses = 0
        self.l.debug(f"trading_expenses: {trading_expenses}")
        trading_outgo = max(trading_allowance, trading_expenses)
        self.l.debug(f"trading_outgo: {trading_outgo}")

        return trading_outgo

    @lru_cache(maxsize=None)
    def get_trading_profit(self):
        self.l.debug("get_trading_profit")
        trading_income = self.get_trading_income()
        self.l.debug(f"trading_income: {trading_income}")
        trading_outgo = self.get_trading_outgo()
        self.l.debug(f"trading_outgo: {trading_outgo}")
        trading_profit = max(0, trading_income - trading_outgo)
        self.l.debug(f"trading_profit: {trading_profit}")
        return trading_profit

    def get_trading_profit_gbp(self):
        return self.gbpb(self.get_trading_profit())

    def get_trading_profit_or_loss_gbp(self):
        profit = self.get_trading_profit()
        if profit > 0:
            return self.get_trading_profit_gbp()
        else:
            return self.get_trading_loss_gbp()

    def get_trading_reduction(self):
        trading_income = self.get_trading_income()
        actual_trading_expenses = self.get_trading_expenses_actual()
        if trading_income <= actual_trading_expenses:
            return actual_trading_expenses
        actual_trading_allowance = self.get_trading_allowance_actual()
        return max(actual_trading_expenses, actual_trading_allowance)

    def get_uk_gains_where_tax_was_not_treated_as_paid(self):
        return self.gbpb(0)

    def get_uk_gains_where_tax_was_treated_as_paid(self):
        return self.gbpb(0)

    def get_uk_patent_royalty_payments_made(self):
        return self.gbpb(0)

    def get_uk_tax_taken_off_total_rents_gbp(self):
        return self.gbpb(0)

    def get_unauthorised_pension_payment_not_surcharged_(self):
        return self.gbpb(0)

    def get_unauthorised_pension_payment_surcharged_(self):
        return self.gbpb(0)

    def get_underpaid_tax(self):
        return self.gbpb(0)

    def get_underpaid_tax_for_earlier_years(self):
        return self.gbpb(0)

    def get_unique_tax_reference(self):
        return self.person.get_unique_tax_reference()

    def get_unique_taxpayer_reference__utr_(self):
        return self.person.get_unique_tax_reference()

    def get_untaxed_foreign_interest(self):
        person_code = self.person_code
        tax_year = self.tax_year
        return self.get_year_category_total(
            tax_year, f"HMRC {person_code} INT income: interest foreign untaxed"
        )

    def get_untaxed_foreign_interest__up_to__2_000__gbp(self):
        untaxed_foreign_interest = self.get_untaxed_foreign_interest()
        return self.gbpb(untaxed_foreign_interest)

    def get_untaxed_uk_interest(self):
        person_code = self.person_code
        tax_year = self.tax_year
        untaxed_uk_interest = self.get_year_category_total(
            tax_year, f"HMRC {person_code} INT income: interest UK untaxed"
        )
        return self.round_down(untaxed_uk_interest)

    def get_untaxed_uk_interest_gbp(self):
        return self.gbpb(self.get_untaxed_uk_interest())

    def get_unused_residential_finance_costs_brought_forward(self):
        return self.gbpb(0)

    def get_unused_residential_finance_costs_brought_forward_gbp(self):
        return self.gbpb(0)

    def get_value_gifted_to_non_uk_charities_in_box_9_and_10(self):
        return self.gbpb(0)

    def get_value_of_land_or_buildings_gifted_to_charities(self):
        return self.gbpb(0)

    def get_value_of_shares_dividends_gifted_to_charities(self):
        return self.gbpb(0)

    def get_vat_registration_threshold(self):
        return self.constants.get_vat_registration_threshold()

    def get_weekly_state_pension(self):
        return self.constants.get_weekly_state_pension()

    def get_weekly_state_pension_forecast(self) -> Decimal:
        weekly_state_pension_forecast = self.person.get_weekly_state_pension_forecast()
        return Decimal(weekly_state_pension_forecast)

    def get_year_category_total(self, tax_year, category):
        return self.transactions.fetch_total_by_tax_year_category(tax_year, category)

    def get_years_voided_isas_held(self):
        return self.gbpb(0)

    def get_your_address(self):
        return self.person.get_address()

    def get_your_date_of_birth(self):
        return self.person.get_uk_date_of_birth()

    def get_your_name_and_address(self):
        return "Leave blank unless changed from previous year"

    def get_your_national_insurance_number(self):
        return self.person.get_national_insurance_number()

    def get_your_phone_number(self):
        return self.person.get_phone_number()

    def get_your_spouse_s_date_of_birth(self) -> str:
        if not self.is_married():
            return ""
        return self.spouse.get_uk_date_of_birth()

    def get_your_spouse_s_first_name(self):
        if not self.is_married():
            return ""
        return self.spouse.get_first_name()

    def get_your_spouse_s_last_name(self):
        if not self.is_married():
            return ""
        return self.spouse.get_last_name()

    def get_your_spouse_s_national_insurance_number(self):
        if not self.is_married():
            return ""
        return self.spouse.get_national_insurance_number()

    def get_zero_emission_car_allowance_gbp(self):
        return ""

    def get_zero_emission_goods_vehicle_allowance_gbp(self):
        return self.gbpb(0)

    def get_zero_emissions_allowance(self):
        return self.gbpb(0)

    def how_many_nic_weeks_in_year(self) -> int:
        return self.constants.how_many_nic_weeks_in_year()

    def is_box_6_blank_as_tax_inc__in_box_2_of__employment_(self):
        return self.gbpb(0)

    def is_married(self) -> bool:
        return self.person.is_married()

    def is_postgraduate_loan_repayment_due(self) -> bool:
        return False

    def is_property_allowance_more_than_property_expenses(self):
        property_allowance = self.get_property_allowance()
        property_expenses = self.get_property_expenses()
        return property_allowance > property_expenses

    def is_property_income_more_than_property_allowance(self):
        property_allowance = self.get_property_allowance()
        property_income = self.get_property_income()
        return property_income > property_allowance

    def is_student_loan_repayment_due(self) -> bool:
        return False

    def is_the_address_shown_above_correct(self):
        return True

    def is_the_basis_period_different_to_the_accounting_period(self):
        return False

    def is_the_estimated_underpaid_tax_amount_correct(self) -> bool:
        return True

    def is_the_underpaid_tax_amount_for_earlier_years_correct(self) -> bool:
        return True

    def is_total_property_income_more_than_property_allowance(self):
        property_income_allowance = self.get_property_income_allowance()
        property_income = self.get_property_income()
        gbp_income = self.gbpb(property_income)
        gbp_allowance = self.gbpb(property_income_allowance)
        if property_income > property_income_allowance:
            return f"Yes: Income {gbp_income} > {gbp_allowance} Property allowance"
        else:
            return f"No: Income {gbp_income} <= {gbp_allowance} Allowance"

    def is_total_trading_income_more_than_trading_allowance(self):
        trading_allowance = self.get_trading_allowance_actual()
        trading_income = self.get_trading_income()
        return trading_income > trading_allowance

    def is_trading_allowance_more_than_trading_expenses(self):
        trading_allowance = self.get_trading_allowance_actual()
        trading_expenses = self.get_trading_expenses_actual()
        return trading_allowance > trading_expenses

    def is_trading_income_more_than_trading_allowance(self):
        trading_allowance = self.get_trading_allowance_actual()
        trading_income = self.get_trading_income()
        return trading_income > trading_allowance

    def is_trading_income_more_than_vat_registration_cusp(self):
        trading_income = self.get_trading_income()
        vat_registration_cusp = self.get_vat_registration_threshold()
        return trading_income > vat_registration_cusp

    def is_your_business_carried_on_abroad(self):
        return False

    def is_your_nominee_your_tax_advisor(self):
        return self.gbpb(0)

    def list_categories(self):
        query = (
            self.transactions.query_builder()
            .select_raw("DISTINCT Category")
            .where(
                f'"Tax year" = "{self.tax_year}" AND "Category" LIKE "HMRC {self.person_code}%" ORDER BY Category'
            )
            .build()
        )
        categories = self.sql.fetch_all(query)
        for row in categories:
            print(row[0])

    def print_reports(self):
        for report_type in HMRC_Output.REPORT_TYPES:
            self.report_type = report_type
            output_details = {
                "answers": self.get_answers(),
                "person_name": self.get_person_name(),
                "report_type": report_type,
                "tax_year": self.tax_year,
                "unique_tax_reference": self.get_unique_tax_reference(),
            }
            hmrc_output = HMRC_Output(output_details)
            hmrc_output.print_report()

    def receives_child_benefit(self):
        return self.person.receives_child_benefit()

    def residence__remittance_basis_etc(self):
        return False

    def round_down(self, amount: Decimal, places: int = 2) -> Decimal:
        return financial_helpers.round_down_decimal(amount, places)

    def round_up(self, amount: Decimal, places: int = 2) -> Decimal:
        return financial_helpers.round_up_decimal(amount, places)

    def should_you_pay_voluntary_class_2_nics__profits___cusp(self) -> bool:
        turnover = self.get_trading_income()
        small_profits_threshold = self.get_small_profits_threshold()
        if turnover > small_profits_threshold:
            return False
        return self.do_you_wish_to_voluntarily_pay_class_2_nics()

    def should_you_pay_voluntary_class_2_nics__turnover___ta(self) -> bool:
        turnover = self.get_trading_income()
        trading_allowance = self.get_trading_allowance_actual()
        if turnover > trading_allowance:
            return False
        return self.do_you_wish_to_voluntarily_pay_class_2_nics()

    def use_property_allowance(self):
        property_allowance = self.get_property_allowance()
        property_expenses = self.get_property_expenses()
        return property_allowance > property_expenses

    def use_trading_allowance(self) -> bool:
        self.l.debug("use_trading_allowance")
        try:
            value = self.use_trading_allowance_override()
            self.l.debug(f"trading allowance override value: {value}")
        except ValueError as v:
            self.l.debug("use_trading_allowance: caught ValueError")
            self.l.exception(v)
            self.l.debug("use_trading_allowance: after v hs been logged")
            trading_allowance = self.get_trading_allowance_actual()
            self.l.debug(f"trading_allowance: {trading_allowance}")
            trading_expenses = self.get_trading_expenses_actual()
            self.l.debug(f"trading_expenses: {trading_expenses}")
            value = trading_allowance > trading_expenses
            self.l.debug(f"2 value: {value}")
        finally:
            self.l.debug("Should always get here")

        return value

    def use_trading_allowance_override(self) -> bool:
        self.l.debug("use_trading_allowance_override")
        try:
            return self.overrides.use_trading_allowance()
        except ValueError as v:
            self.l.info(v)
            raise

    def were_any_repayments_claimed_for_next_year(self):
        return False

    def were_any_results_already_declared_on_a_previous_return(self):
        return False

    def were_there_income_tax_losses(self):
        return False

    def were_you_employed_in_this_tax_year(self) -> bool:
        person_code = self.person.code
        tax_year = self.tax_year
        query = (
            self.transactions.query_builder()
            .select_raw("COUNT(*)")
            .where(
                f'"Tax year"="{tax_year}" AND "Category" LIKE "HMRC {person_code} EMP%income"'
            )
            .build()
        )
        how_many = self.sql.fetch_one_value(query)
        return how_many > 0

    def were_you_in_partnership_s__this_tax_year(self):
        return False

    def were_you_not_resident_in_uk_during_the_tax_year(self):
        return False

    def were_you_over_state_pension_age_at_tax_year_start(self):
        return False

    def were_you_self_employed_in_this_tax_year(self) -> bool:
        how_many = self.get_how_many_businesses()
        return how_many > 0

    def were_you_under_16_at_tax_year_start(self):
        return False

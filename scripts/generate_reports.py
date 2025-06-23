from scripts.bootstrap import setup_path

setup_path()

from datetime import datetime

from finances.classes.hmrc import HMRC
from finances.classes.table_hmrc_questions_by_year import HMRC_QuestionsByYear


def check_questions(tax_year: str) -> None:
    questions = HMRC_QuestionsByYear(tax_year)
    print("Checking questions")
    questions.check_questions()


def get_tax_years_from(earliest_year: int) -> list[str]:
    current_year = datetime.now().year
    years_to_report = list(range(earliest_year, current_year))

    tax_years = [f"{year} to {year + 1}" for year in years_to_report]

    return tax_years


def print_reports(hmrc_people: list[str], tax_year: str) -> None:
    for person in hmrc_people:
        hmrc = HMRC(person, tax_year)
        hmrc.print_reports()


def main() -> None:
    # List of people to generate reports for
    hmrc_people = ["S", "B"]

    earliest_year = 2023

    tax_years = get_tax_years_from(earliest_year)

    for tax_year in tax_years:
        # Tax year to generate reports for

        check_questions(tax_year)

        print_reports(hmrc_people, tax_year)


if __name__ == "__main__":
    main()

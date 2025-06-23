from dataclasses import dataclass
from functools import cache
from typing import Any

from finances.util.string_helpers import crop


def format_answer(answer: Any) -> str:
    if isinstance(answer, bool):
        return "Yes" if answer else "No"
    if isinstance(answer, float):
        return f"£{answer:,.2f}"
    if isinstance(answer, int):
        return f"{answer:,}"
    return str(answer)


class HTMLOutputError(Exception):
    pass


@dataclass(frozen=True)
class HMRCOutputData:
    person_name: str
    report_type: str
    tax_year: str
    unique_tax_reference: str
    answers: list[list[str]]


class HMRCOutput:
    HMRC_CALCULATION = "calculation"
    HMRC_ONLINE_ANSWERS = "online answers"
    HMRC_TAX_RETURN = "tax return"
    REPORT_TYPES = [HMRC_CALCULATION, HMRC_ONLINE_ANSWERS, HMRC_TAX_RETURN]

    def __init__(
        self, hmrc_output_data:HMRCOutputData
    ) -> None:
        self.person_name = hmrc_output_data.person_name
        self.report_type = hmrc_output_data.report_type
        self.tax_year = hmrc_output_data.tax_year
        self.unique_tax_reference = hmrc_output_data.unique_tax_reference
        self.answers = hmrc_output_data.answers

        self.previous_section = ""
        self.previous_header = ""

    def get_title(self) -> str:
        unique_tax_reference = self.unique_tax_reference
        person_name = self.person_name
        report_type = self.report_type
        tax_year = self.tax_year
        return f"HMRC {report_type} {tax_year} for {person_name} - UTR {unique_tax_reference}\n"

    def position_answer(self, string_list: list[str]) -> str:
        if self.report_type == HMRCOutput.HMRC_ONLINE_ANSWERS:
            widths = [55]
        else:
            widths = [5, 60]
        how_many = len(widths)
        formatted_parts = [
            f"{string:<{width}}"
            for (string, width) in zip(string_list[:how_many], widths)
        ]
        try:
            return "".join(formatted_parts) + string_list[how_many]
        except IndexError:
            raise HTMLOutputError("Answer formatting error: string_list is too short.")

    def print(self, txt: str) -> None:
        with open(self.get_report_name(), "a") as file:
            print(txt, file=file)

    def print_end_of_tax_return(self) -> None:
        title = self.get_title()
        self.print(f"\nEnd of {title}")

    def print_formatted_answer(
        self,
        question: str,
        section: str,
        header: str,
        box: str,
        answer: Any,
        information: str,
    ) -> None:
        if section != self.previous_section:
            self.previous_section = section
            self.print(f"\n\n{section.upper()}\n")

        if header != self.previous_header:
            self.previous_header = header
            self.print(f"\n{header.upper()}\n")

        formatted_answer = format_answer(answer)

        box = crop(box, " (GBP)")

        if self.report_type == HMRCOutput.HMRC_ONLINE_ANSWERS:
            positioned_answer = self.position_answer([box, formatted_answer])
        else:
            positioned_answer = self.position_answer([box, question, formatted_answer])

        if len(information):
            self.print(information)

        self.print(positioned_answer)

    def print_report(self) -> None:
        report_type = self.report_type
        if not report_type:
            raise ValueError("Invalid report type provided.")

        answers = self.answers
        if len(answers) == 0:
            print("No answers found ==> No report generated.")
            return

        self.truncate_report()
        self.print_title()
        for answer_number, (
            question,
            section,
            header,
            box,
            answer,
            information,
        ) in enumerate(answers, start=1):
            self.print_formatted_answer(
                question, section, header, box, answer, information
            )
        self.print_end_of_tax_return()

    def print_title(self) -> None:
        self.print(self.get_title())
        self.previous_section = ""
        self.previous_header = ""

    @cache
    def get_report_name(self) -> str:
        """
        Gets the report file name based on the person's name, report type, and tax year.
        """
        report_dir = "output/reports/hmrc"
        # Retrieve necessary information
        person_name = self.person_name
        report_type = self.report_type
        tax_year = self.tax_year

        # Generate a sanitized file name
        sanitized_name = person_name.replace(" ", "_").lower()
        sanitized_report_type = report_type.replace(" ", "_").lower()
        sanitized_tax_year = tax_year.replace(" ", "_")

        report_name = (
            f"{report_dir}/{sanitized_tax_year}_{sanitized_name}_{sanitized_report_type}.txt"
        )
        return report_name

    def print_report_name(self) -> None:
        # Log the generated file name
        print(f"Generated report file name: {self.get_report_name()}")

    def truncate_report(self) -> None:
        """
        Creates an empty file with the report name, overwriting if it already exists.
        """

        report_name = self.get_report_name()

        # Create or overwrite the file to ensure it's empty
        try:
            with open(report_name, "w"):
                pass  # Truncate the file if it exists, or create it if it doesn't
        except Exception as e:
            raise HTMLOutputError(
                f"Failed to create the report file: {report_name}"
            ) from e

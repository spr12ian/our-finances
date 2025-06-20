from typing import Any

import finances.util.financial_helpers as uf


class HMRC_Output:
    HMRC_CALCULATION = "calculation"
    HMRC_ONLINE_ANSWERS = "online answers"
    HMRC_TAX_RETURN = "tax return"
    REPORT_TYPES = [HMRC_CALCULATION, HMRC_ONLINE_ANSWERS, HMRC_TAX_RETURN]

    def __init__(self, output_details: dict[str,str])->None:
        self.answers = output_details["answers"]
        self.person_name = output_details["person_name"]
        self.report_type = output_details["report_type"]
        self.tax_year = output_details["tax_year"]
        self.unique_tax_reference = output_details["unique_tax_reference"]

        self.previous_section = ""
        self.previous_header = ""

    def get_title(self) -> Any:
        unique_tax_reference = self.unique_tax_reference
        person_name = self.person_name
        report_type = self.report_type
        tax_year = self.tax_year
        return f"HMRC {report_type} {tax_year} for {person_name} - UTR {unique_tax_reference}\n"

    def position_answer(self, string_list:str) -> str:
        if self.report_type == HMRC_Output.HMRC_ONLINE_ANSWERS:
            widths = [55]
        else:
            widths = [5, 60]
        how_many = len(widths)
        formatted_parts = [
            f"{string:<{width}}"
            for (string, width) in zip(string_list[:how_many], widths)
        ]
        return "".join(formatted_parts) + string_list[how_many]

    def print(self, txt: str)->None:
        report_file_name = self.report_file_name
        with open(report_file_name, "a") as file:
            print(txt, file=file)

    def print_end_of_tax_return(self) -> Any:
        title = self.get_title()
        self.print(f"\nEnd of {title}")

    def print_formatted_answer(
        self, question, section: str, header: str, box, answer, information
    )->None:
        if section != self.previous_section:
            self.previous_section = section
            self.print(f"\n\n{section.upper()}\n")
        if header != self.previous_header:
            self.previous_header = header
            self.print(f"\n{header.upper()}\n")
        if isinstance(answer, bool):
            answer = "Yes" if answer else "No"
        elif isinstance(answer, float):
            answer = f"£{answer:,.2f}"
        elif isinstance(answer, int):
            answer = f"{answer:,}"
        elif isinstance(answer, str):
            pass
        else:
            answer = str(answer)
        box = uf.crop(box, " (GBP)")
        if self.report_type == HMRC_Output.HMRC_ONLINE_ANSWERS:
            formatted_answer = self.position_answer([box, answer])
        else:
            formatted_answer = self.position_answer([box, question, answer])
        if len(information):
            self.print(information)
        self.print(formatted_answer)

    def print_report(self) -> Any:
        report_type = self.report_type
        if not isinstance(report_type, str) or not report_type:
            raise ValueError("Invalid report type provided.")
        answers = self.answers
        if not answers:
            self.l.warning("No answers found ==> No report generated.")
            return
        self.set_report_name()
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

    def set_report_name(self) -> Any:
        """
        Sets the report file name based on the person's name, report type, and tax year,
        and creates an empty file with the generated name, overwriting if it already exists.
        """
        # Retrieve necessary information
        person_name = self.person_name
        report_type = self.report_type
        tax_year = self.tax_year

        # Validate inputs
        if not person_name or not isinstance(person_name, str):
            raise ValueError("Invalid person name.")
        if not report_type or not isinstance(report_type, str):
            raise ValueError("Invalid report type.")
        if not tax_year or not isinstance(tax_year, str):
            raise ValueError("Invalid tax year.")

        # Generate a sanitized file name
        sanitized_name = person_name.replace(" ", "_").lower()
        sanitized_report_type = report_type.replace(" ", "_").lower()
        sanitized_tax_year = tax_year.replace(" ", "_")

        report_file_name = (
            f"hmrc_{sanitized_report_type}_{sanitized_tax_year}_{sanitized_name}.txt"
        )

        # Log the generated file name
        print(f"Generated report file name: {report_file_name}")

        # Create or overwrite the file to ensure it's empty
        try:
            with open(report_file_name, "w") as file:
                pass  # This will truncate the file if it exists, or create it if it doesn't
        except Exception as e:
            self.l.error(f"Failed to create the report file: {e}")
            raise

        # Save the report file name
        self.report_file_name = report_file_name

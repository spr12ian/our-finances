from typing import Any

from finances.classes.sqlite_helper import (
    to_table_name,
    validate_column_name,
)
from finances.classes.sqlite_table import SQLiteTable
from finances.util.string_helpers import crop, to_method_name


class HMRC_QuestionsByYear(SQLiteTable):
    yes_no_questions = [
        "Are ",
        "Did ",
        "Do ",
        "Does ",
        "Has ",
        "Have ",
        "Is ",
        "Should ",
        "Use ",
        "Was ",
        "Were ",
    ]

    def _get_table_name(self, tax_year: str) -> str:
        sanitised_tax_year = to_table_name(tax_year)

        table_name = f"hmrc_questions{sanitised_tax_year}"

        return table_name

    def __init__(self, tax_year: str) -> None:
        table_name = self._get_table_name(tax_year)

        super().__init__(table_name)

    def _get_questions(self, columns: list[str], order_column: str) -> list[list[str]]:
        for col in columns:
            validate_column_name(col)
        validate_column_name(order_column)
        table_name = self.table_name

        columns_as_string = self.convert_columns_to_string(columns)

        query = (
            f'SELECT {columns_as_string}, q2."additional_information"'
            + f" FROM {table_name} q1 JOIN hmrc_questions q2"
            + " ON q1.question = q2.question"
            + f' WHERE q1."{order_column}" > 0'
            + f' ORDER BY q1."{order_column}" ASC'
        )

        questions: list[list[str]] = [
            [
                row[0],  # question
                row[1],  # section
                row[2],  # header
                row[3],  # box
                self.to_method_name(row[0]),  # method
                row[4],  # additional information
            ]
            for row in self.sql.fetch_all(query)
        ]

        return questions

    def convert_columns_to_string(self, columns: list[str]) -> str:
        return ", ".join([f'q1."{column}"' for column in columns])

    def check_questions(self) -> None:
        self.list_unused_questions()

        self.list_online_questions_not_in_printed_form()

    def list_online_questions_not_in_printed_form(self) -> None:
        table_name = self.table_name
        query = (
            'SELECT q1.question, q1."online_order", q2."printed_order"'
            + f" FROM {table_name} q1 JOIN {table_name} q2"
            + " WHERE q1.question = q2.question"
            + ' AND q1."online_order" > 0'
            + ' AND q2."online_order" = 0'
        )
        rows = self.sql.fetch_all(query)
        how_many_rows = len(rows)
        if how_many_rows > 0:
            for row in rows:
                print(row)

    def list_unused_questions(self) -> None:
        table_name = self.table_name
        core_questions = "hmrc_questions"
        query = (
            "SELECT q1.question"
            + f" FROM {core_questions} q1 LEFT JOIN {table_name} q2"
            + " ON q1.question = q2.question"
            + " WHERE q2.question IS NULL"
        )
        rows = self.sql.fetch_all(query)
        how_many_rows = len(rows)
        if how_many_rows > 0:
            print(
                f"{how_many_rows} unused questions in {core_questions} but not in {table_name}"
            )
            for row in rows:
                print(row)

    def get_hmrc_calculation_questions(self) -> Any:
        questions = [
            [
                "",  # question
                "",  # section
                "",  # header
                "",  # box
                "get_hmrc_calculation",  # method
                "",  # additional information
            ]
        ]
        return questions

    def get_online_questions(self) -> Any:
        columns = [
            "question",
            "online_section",
            "online_header",
            "online_box",
        ]
        order_column = "online_order"
        return self._get_questions(columns, order_column)

    def get_printed_form_questions(self) -> Any:
        columns = ["question", "printed_section", "printed_header", "printed_box"]
        order_column = "printed_order"
        return self._get_questions(columns, order_column)

    def is_it_a_yes_no_question(self, question: str) -> bool:
        return any(question.startswith(q) for q in self.yes_no_questions)

    def to_method_name(self, question: str) -> str:
        reformatted_question = to_method_name(question)

        if self.is_it_a_yes_no_question(question):
            method_name = reformatted_question
        elif question[-6:] == " (GBP)":
            method_name = "get_" + crop(reformatted_question, "__gbp_") + "_gbp"
        else:
            method_name = "get_" + reformatted_question

        return method_name

import our_finances.util.financial_helpers as uf
from sqlalchemy_helper import valid_sqlalchemy_name, validate_sqlalchemy_name

from finances.classes.sqlite_table import SQLiteTable


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

    def _get_table_name(self, tax_year):
        sanitised_tax_year = valid_sqlalchemy_name(tax_year)

        table_name = f"hmrc_questions{sanitised_tax_year}"

        return table_name

    def __init__(self, tax_year):
        self.l = LogHelper("HMRC_QuestionsByYear")
        # self.l.set_level_debug()
        self.l.debug(__file__)
        self.l.debug(__class__)
        self.l.debug(__name__)

        table_name = self._get_table_name(tax_year)

        super().__init__(table_name)

        self.l.debug(f"table_name: {table_name}")
        self.l.debug(f"self.yes_no_questions: {self.yes_no_questions}")

    def _get_questions(self, columns, order_column):
        self.l.debug(f"columns: {columns}")
        self.l.debug(f"order_column: {order_column}")
        [validate_sqlalchemy_name(col) for col in columns]
        validate_sqlalchemy_name(order_column)
        table_name = self.table_name

        columns_as_string = self.convert_columns_to_string(columns)

        query = (
            f'SELECT {columns_as_string}, q2."additional_information"'
            + f" FROM {table_name} q1 JOIN hmrc_questions q2"
            + " ON q1.question = q2.question"
            + f' WHERE q1."{order_column}" > 0'
            + f' ORDER BY q1."{order_column}" ASC'
        )

        self.l.debug(f"query: {query}")

        questions = [
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

    def convert_columns_to_string(self, columns):
        return ", ".join([f'q1."{column}"' for column in columns])

    def check_questions(self):
        self.l.debug("check_questions")

        self.list_unused_questions()

        self.list_online_questions_not_in_printed_form()

    def list_online_questions_not_in_printed_form(self):
        self.l.debug("list_online_questions_not_in_printed_form")
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
            self.l.debug(f"{how_many_rows} online questions not in printed form")
            self.l.debug(query)
            for row in rows:
                self.l.debug(row)

    def list_unused_questions(self):
        self.l.debug("list_unused_questions")
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
            self.l.info(f"{how_many_rows} unused questions")
            self.l.debug(query)
            for row in rows:
                self.l.info(row)

    def get_hmrc_calculation_questions(self):
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

    def get_online_questions(self):
        columns = [
            "question",
            "online_section",
            "online_header",
            "online_box",
        ]
        order_column = "online_order"
        return self._get_questions(columns, order_column)

    def get_printed_form_questions(self):
        self.l.debug("get_printed_form_questions")
        columns = ["question", "printed_section", "printed_header", "printed_box"]
        order_column = "printed_order"
        return self._get_questions(columns, order_column)

    def is_it_a_yes_no_question(self, question):
        return any(question.startswith(q) for q in self.yes_no_questions)

    def to_method_name(self, question):
        self.l.debug("to_method_name")
        self.l.debug(f"question: {question}")
        reformatted_question = uf.to_valid_method_name(question)
        self.l.debug(f"reformatted_question: {reformatted_question}")

        if self.is_it_a_yes_no_question(question):
            self.l.debug(f"Yes/No question: {question}")
            method_name = reformatted_question
        elif question[-6:] == " (GBP)":
            self.l.debug(" (GBP) matched")
            method_name = "get_" + uf.crop(reformatted_question, "__gbp_") + "_gbp"
        else:
            method_name = "get_" + reformatted_question

        self.l.debug(f"method_name: {method_name}")

        return method_name

from typing import Any
from finances.classes.sqlite_table import SQLiteTable


class Categories(SQLiteTable):
    def __init__(self, category: str | None = None):
        super().__init__("categories")
        self.category = category

    def fetch_by_category(self, category):
        query = self.query_builder().where(f"category = '{category}'").build()
        return self.sql.fetch_all(query)

    def fetch_by_hmrc_page_id(self, hmrc_page, hmrc_question_id, person_code):
        query = (
            self.query_builder()
            .select("category")
            .where(
                f'"hmrc_page"="{hmrc_page}" AND "hmrc_question_id"="{hmrc_question_id}" AND "category" LIKE "HMRC {person_code}%"'
            )
            .build()
        )
        return self.sql.fetch_one_value(query)

    def get_description(self) -> Any:
        return self.get_value_by_category("description")

    def get_category_group(self) -> Any:
        return self.get_value_by_category("category_group")

    def get_value_by_category(self, column_name):
        if self.category:
            query = (
                self.query_builder()
                .select(column_name)
                .where(f'"category" = "{self.category}"')
                .build()
            )
            result = self.sql.fetch_one_value(query)
        else:
            result = None

        return result

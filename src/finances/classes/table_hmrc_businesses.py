from finances.classes.sqlite_table import SQLiteTable


class HMRC_Businesses(SQLiteTable):
    def __init__(self, business_name: str):
        super().__init__("hmrc_businesses")
        self.business_name = business_name

    def get_business_description(self) -> Any:
        business_description = self._get_value_by_business_name("business_description")

        return business_description

    def get_business_name(self) -> Any:
        return self.business_name

    def get_business_postcode(self) -> Any:
        business_description = self._get_value_by_business_name("business_postcode")

        return business_description

    def _get_value_by_business_name(self, column_name):
        business_name = self.business_name
        query = (
            self.query_builder()
            .select(column_name)
            .where(f'"business_name" = "{business_name}"')
            .build()
        )

        result = self.sql.fetch_one_value(query)

        if result is None:
            raise ValueError(
                f"Could not find '{column_name}' for business {business_name}"
            )

        return result

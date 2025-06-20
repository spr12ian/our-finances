from finances.classes.sqlite_table import SQLiteTable


class HMRC_Property(SQLiteTable):
    def _get_value_by_postcode_column(self, column_name):
        postcode = self.postcode
        if postcode:
            query = (
                self.query_builder()
                .select(column_name)
                .where(f'"property_postcode" = "{postcode}"')
                .build()
            )
            result = str(self.sql.fetch_one_value(query))
        else:
            raise ValueError(f"Unexpected postcode: {postcode}")

        return result

    def __init__(self, postcode):
        super().__init__("hmrc_property")
        self.postcode = postcode

    def fetch_by_postcode(self, postcode):
        query = self.query_builder().where(f"postcode = '{postcode}'").build()
        return self.sql.fetch_all(query)

    def get_property_postcode(self) -> str:
        return self.postcode

    def get_property_owner_code(self) -> str:
        return self._get_value_by_postcode_column("property_owner_code")

    def get_property_ownership_share(self) -> float:
        return self._get_value_by_postcode_column("property_ownership_share")

    def get_property_joint_owner_code(self) -> str:
        property_joint_owner_code = self._get_value_by_postcode_column(
            "property_joint_owner_code"
        )
        return property_joint_owner_code

    def is_let_jointly(self) -> bool:
        return self.get_property_joint_owner_code() != ""

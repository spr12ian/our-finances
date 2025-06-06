from sqlalchemy_helper import validate_sqlalchemy_name

class QueryBuilder:
    def __init__(self, table_name:str):
        self.table_name = table_name
        self.columns = []
        self.conditions = []
        self.group_by = []
        self.order_by = None
        self.limit = None

    def select(self, *columns):
        [validate_sqlalchemy_name(col) for col in columns]
        self.columns = [f'"{col}"' for col in columns]
        return self

    def select_raw(self, select_str:str):
        self.columns = [select_str]
        return self

    def total(self, column:str):
        validate_sqlalchemy_name(column)
        self.columns = [f'COALESCE(SUM("{column}"), 0)']
        return self

    def where(self, condition):
        self.conditions.append(condition)
        return self

    def order(self, column:str, direction:str="ASC"):
        validate_sqlalchemy_name(column)
        self.order_by = f'"{column}" {direction}'
        return self

    def set_limit(self, limit):
        self.limit = limit
        return self

    def build(self)-> str:
        columns = ", ".join(self.columns) if self.columns else "*"

        query = f"SELECT {columns} FROM {self.table_name}"

        if self.conditions:
            conditions = " AND ".join(self.conditions)
            query += f" WHERE {conditions}"

        if self.order_by:
            query += f" ORDER BY {self.order_by}"

        if self.limit:
            query += f" LIMIT {self.limit}"

        return query

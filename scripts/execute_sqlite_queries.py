from sqlalchemy_helper import SQLAlchemyHelper
from sqlalchemy import text

with open("queries.sql", "r") as file:
    queries = file.read().split(";")

sql = SQLAlchemyHelper()
session = sql.get_session()

for query in queries:
    if query.strip():
        print(query)
        result = session.execute(text(query))
        for row in result:
            print(row)

from sqlalchemy import text
from sqlalchemy_helper import SQLAlchemyHelper

with open("queries.sql") as file:
    queries = file.read().split(";")

sql = SQLAlchemyHelper()
session = sql.get_session()

for query in queries:
    if query.strip():
        print(query)
        result = session.execute(text(query))
        for row in result:
            print(row)

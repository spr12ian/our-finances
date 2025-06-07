import sqlalchemy
from sqlalchemy import create_engine

engine = create_engine("sqlite:///our_finances.sqlite", echo=True)


def get_engine() -> sqlalchemy.engine.Engine:
    from sqlalchemy import create_engine

    return create_engine("sqlite:///our_finances.sqlite", echo=True)


def print_version() -> None:
    print(sqlalchemy.__version__)


def test_text() -> None:
    from sqlalchemy import text

    with get_engine().connect() as conn:
        result = conn.execute(text("select 'hello world'"))
        print(result.all())

        conn.commit()  # Neccessary with engine.connect

    with get_engine().begin() as conn:
        result = conn.execute(text('select * from "People"'))
        print(result.all())

    with get_engine().begin() as conn:
        result = conn.execute(text("SELECT Code, Person FROM People"))
        for row in result:
            print(f"Code: {row.Code}  Person: {row.Person}")

    with get_engine().begin() as conn:
        result = conn.execute(text("SELECT Code, Person FROM People"))
        for Code, Person in result:
            print(f"Code: {Code}  Person: {Person}")

    with get_engine().begin() as conn:
        result = conn.execute(text("SELECT Code, Person FROM People"))
        for row in result:
            Code, Person = row.Code, row.Person
            print(f"Code: {Code}  Person: {Person}")

    with get_engine().begin() as conn:
        result = conn.execute(text("SELECT Code, Person FROM People"))
        for row in result:
            Code, Person = row
            print(f"Code: {Code}  Person: {Person}")

    with get_engine().begin() as conn:
        result = conn.execute(
            text("SELECT Code, Person FROM People WHERE Code = :code"), {"code": "S"}
        )
        for Code, Person in result:
            print(f"Code: {Code}  Person: {Person}")


def create_some_table() -> None:
    from sqlalchemy import text

    with get_engine().begin() as conn:
        conn.execute(text("CREATE TABLE some_table (x int, y int)"))
        conn.execute(
            text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
            [{"x": 1, "y": 1}, {"x": 2, "y": 4}],
        )
        conn.execute(
            text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
            [{"x": 6, "y": 8}, {"x": 9, "y": 10}],
        )


def test_session() -> None:
    from sqlalchemy import text
    from sqlalchemy.orm import Session

    stmt = text("SELECT x, y FROM some_table WHERE y > :y ORDER BY x, y")
    with Session(engine) as session:
        result = session.execute(stmt, {"y": 6})
        for row in result:
            print(f"x: {row.x}  y: {row.y}")

    with Session(engine) as session:
        result = session.execute(
            text("UPDATE some_table SET y=:y WHERE x=:x"),
            [{"x": 9, "y": 11}, {"x": 13, "y": 15}],
        )
        session.commit()


test_session()

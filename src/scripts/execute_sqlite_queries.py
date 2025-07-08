#!/usr/bin/env python3

import sqlite3
import sys

import sqlparse

from finances.classes.config import Config

if len(sys.argv) < 2:
    print("Usage: python script.py <filename.sql>")
    sys.exit(1)

filename = sys.argv[1]
print(f"Input file: {filename}")
with open(filename, encoding="utf-8") as file:
    script = file.read()

config = Config()

conn = sqlite3.connect(config.OUR_FINANCES_SQLITE_DB_NAME)
cursor = conn.cursor()

# Split script into individual statements safely
statements = sqlparse.split(script)

for statement in statements:
    stmt = statement.strip()
    if not stmt:
        continue
    stmt = sqlparse.format(  # type: ignore
        stmt, reindent=True, keyword_case="upper", strip_comments=True
    )
    print(f"Executing:\n{stmt}")
    try:
        cursor.execute(stmt)
        if stmt.startswith("SELECT"):
            rows = cursor.fetchall()
            print(f"Returned {len(rows)} row(s):")
            for row in rows:
                print(row)
        else:
            conn.commit()
    except Exception as e:
        print(f"⚠️ Error: {e}")
        conn.rollback()

cursor.close()
conn.close()

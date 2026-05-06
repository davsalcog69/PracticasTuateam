from sqlalchemy import create_engine, text
import os

DATABASE_URL = "sqlite:///marketplace.db"
engine = create_engine(DATABASE_URL)

with engine.connect() as con:
    result = con.execute(text("SELECT username, email FROM users"))
    for row in result:
        print(f"User: {row[0]}, Email: {row[1]}")

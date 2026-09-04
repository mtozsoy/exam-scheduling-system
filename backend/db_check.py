import sys
import os
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.db.database import engine

def list_tables():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'"))
        for row in result:
            print(row[0])

if __name__ == "__main__":
    list_tables()

import urllib.request
from sqlalchemy import create_engine, MetaData
from app.db.database import SQLALCHEMY_DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
metadata = MetaData()
metadata.reflect(bind=engine)

for table in metadata.tables.values():
    print(table.name)
    for column in table.columns:
        print(f"  - {column.name}: {column.type}")

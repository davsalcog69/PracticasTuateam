
from sqlalchemy import create_engine, inspect
import os

db_url = "postgresql://postgres.fenlzmyffahriefuljom:p6JmSE8wTDPZkkDS@aws-1-eu-west-2.pooler.supabase.com:6543/postgres"
engine = create_engine(db_url)
inspector = inspect(engine)

for table_name in ["cars", "car_export"]:
    print(f"\nTable: {table_name}")
    columns = inspector.get_columns(table_name)
    for column in columns:
        print(f" - {column['name']}: {column['type']}")

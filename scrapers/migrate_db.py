
from sqlalchemy import create_engine, text
import os

db_url = "postgresql://postgres.fenlzmyffahriefuljom:p6JmSE8wTDPZkkDS@aws-1-eu-west-2.pooler.supabase.com:6543/postgres"
engine = create_engine(db_url)

with engine.connect() as conn:
    print("Migrating database...")
    try:
        conn.execute(text("ALTER TABLE cars ADD COLUMN IF NOT EXISTS source_url TEXT;"))
        print(" - Added source_url to 'cars'")
    except Exception as e:
        print(f" - Error in 'cars': {e}")

    try:
        conn.execute(text("ALTER TABLE car_export ADD COLUMN IF NOT EXISTS source_url TEXT;"))
        print(" - Added source_url to 'car_export'")
    except Exception as e:
        print(f" - Error in 'car_export': {e}")
    
    conn.commit()
    print("Migration complete.")

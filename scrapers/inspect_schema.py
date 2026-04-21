import os
import sys
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker

# ROOT fix
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_ROOT = os.path.join(ROOT, "backend")
if ROOT not in sys.path: sys.path.insert(0, ROOT)
if BACKEND_ROOT not in sys.path: sys.path.insert(0, BACKEND_ROOT)

try:
    from backend.core.config import settings
    DATABASE_URL = settings.DATABASE_URL
    print(f"DATABASE: {DATABASE_URL.split('@')[-1]}")
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    for table in ['dubicars', 'cars']:
        print(f"\n--- Checking Table: {table} ---")
        try:
            # Check schema
            query = text(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}'")
            res = session.execute(query)
            cols = res.fetchall()
            if not cols:
                print(f"ERROR: Table '{table}' NOT FOUND.")
            else:
                # Count
                count_res = session.execute(text(f"SELECT count(*) FROM {table}"))
                print(f"Rows: {count_res.scalar()}")
                print("Columns:")
                for col in cols:
                    print(f" - {col[0]} ({col[1]})")
        except Exception as te:
            print(f"Error accessing {table}: {te}")

    session.close()
except Exception as e:
    print(f"General Error: {e}")

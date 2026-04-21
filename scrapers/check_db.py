import os
import sys
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker

# ROOT fix
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    from backend.core.config import settings
    DATABASE_URL = settings.DATABASE_URL
    print(f"Using DATABASE_URL: {DATABASE_URL}")
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    # 1. Check if table exists and count rows
    try:
        res = session.execute(text("SELECT count(*) FROM dubicars"))
        count = res.scalar()
        print(f"Row count in 'dubicars': {count}")
    except Exception as e:
        print(f"Error checking 'dubicars' table: {e}")
        
    # 2. Check schema of 'dubicars'
    try:
        res = session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'dubicars'"))
        cols = [r[0] for r in res]
        print(f"Columns in 'dubicars': {cols}")
    except Exception as e:
        print(f"Error checking columns: {e}")

    session.close()
except Exception as e:
    print(f"General Error: {e}")

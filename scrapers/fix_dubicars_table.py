import os
import sys
from sqlalchemy import text, create_engine

# ROOT fix
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_ROOT = os.path.join(ROOT, "backend")
if ROOT not in sys.path: sys.path.insert(0, ROOT)
if BACKEND_ROOT not in sys.path: sys.path.insert(0, BACKEND_ROOT)

try:
    from backend.core.config import settings
    DATABASE_URL = settings.DATABASE_URL
    print(f"Connecting to: {DATABASE_URL.split('@')[-1]}")
    
    engine = create_engine(DATABASE_URL)
    
    # Use engine.begin() to ensure AUTO-COMMIT at the end of block
    with engine.begin() as conn:
        print("Dropping and recreating 'dubicars' table with correct schema...")
        
        # 1. Drop
        conn.execute(text("DROP TABLE IF EXISTS dubicars CASCADE;"))
        
        # 2. Create matching 'cars' schema but for dubicars
        conn.execute(text("""
            CREATE TABLE dubicars (
                id VARCHAR PRIMARY KEY,
                portal TEXT,
                brand VARCHAR,
                model VARCHAR,
                year INTEGER,
                kilometrage INTEGER,
                mileage INTEGER,
                fuel TEXT,
                power INTEGER,
                price DOUBLE PRECISION,
                currency TEXT,
                country VARCHAR,
                location TEXT,
                url VARCHAR,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))
        print("Table 'dubicars' creation query executed and committed.")

    # Re-verify in a new session
    with engine.begin() as conn:
        print("Re-verifying table schema...")
        query = text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'dubicars' ORDER BY column_name")
        res = conn.execute(query)
        for row in res:
            print(f" - {row[0]}: {row[1]}")

    print("Table 'dubicars' is now READY.")

except Exception as e:
    print(f"Error: {e}")
